
import sys
import re
from concurrent import futures
from datetime import datetime, timedelta

import grpc
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError

sys.path.insert(0, r"C:\Users\lotus\project")

from database import SessionLocal

from tables.user import User
from tables.blog import Blog
from tables.category import Category
from tables.file import File
from tables.tag import Tag
from tables.blog_tag import BlogTag

from service.file_service import FileServiceClient

import blog_pb2
import blog_pb2_grpc


class BlogService(blog_pb2_grpc.BlogServiceServicer):

    def slugify(self, text):
        text = (text or "").lower().strip()
        text = re.sub(r"[^a-z0-9]+", "-", text)
        return text.strip("-")

    def generate_unique_slug(self, db, slug):
        base_slug = self.slugify(slug)

        if not base_slug:
            base_slug = "blog"

        unique_slug = base_slug
        counter = 2

        while db.query(Blog).filter(
            Blog.slug == unique_slug
        ).first():
            unique_slug = f"{base_slug}-{counter}"
            counter += 1

        return unique_slug

    def get_photo_path(self, file_id):
        if not file_id:
            return ""

        client = FileServiceClient("localhost:5055")

        try:
            file_data = client.get_file(file_id)

            photo_path = (
                getattr(file_data, "optimized_file_url", "")
                or getattr(file_data, "original_file_url", "")
                or getattr(file_data, "url", "")
            )

            print(
                f"File ID: {file_id}, "
                f"Photo path: {photo_path}"
            )

            return photo_path

        except grpc.RpcError as exc:
            print(
                f"Could not get photo for file_id={file_id}: {exc}"
            )
            return ""

        finally:
            client.close()

    def validate_file(self, file_id, context):
        if not file_id:
            return

        client = FileServiceClient("localhost:5055")

        try:
            client.get_file(file_id)

        except grpc.RpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    f"File ID {file_id} not found in File Service"
                )

            context.abort(
                grpc.StatusCode.UNAVAILABLE,
                "Could not connect to File Service"
            )

        finally:
            client.close()

    def add_category_and_tags(self, blog_response, blog):
        # افزودن دسته‌بندی
        if blog.category:
            blog_response.category.id = blog.category.id
            blog_response.category.name = blog.category.name

        # افزودن تگ‌ها
        for tag in blog.tags:
            tag_response = blog_response.tags.add()
            tag_response.id = tag.id
            tag_response.name = tag.name

        return blog_response

    def GetBlogs(self, request, context):
        print("GetBlogs request received by gRPC server")
        db: Session = SessionLocal()

        try:
            blogs = (
                db.query(Blog)
                .options(
                    selectinload(Blog.category),
                    selectinload(Blog.tags),
                )
                .all()
            )

            response = blog_pb2.BlogList()
            now = datetime.now()

            for blog in blogs:
                last_view = blog.last_view_at

                if (
                    last_view is None
                    or now - last_view >= timedelta(minutes=1)
                ):
                    blog.view_num = (blog.view_num or 0) + 1
                    blog.last_view_at = now

            db.commit()

            for blog in blogs:
                blog_response = response.blogs.add(
                    id=blog.id,
                    title=blog.title,
                    file_id=blog.file_id or 0,
                    slug=blog.slug or "",
                    description=blog.description or "",
                    content=blog.content or "",
                    user_id=blog.user_id or 0,
                    view_num=blog.view_num or 0,
                    path_photo=self.get_photo_path(blog.file_id)
                )

                self.add_category_and_tags(
                    blog_response,
                    blog
                )

            return response

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    def GetBlog(self, request, context):
        print("GetBlog request received by gRPC server")
        db: Session = SessionLocal()

        try:
            blog = (
                db.query(Blog)
                .options(
                    selectinload(Blog.category),
                    selectinload(Blog.tags),
                )
                .filter(Blog.id == request.blog_id)
                .first()
            )

            if not blog:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Blog not found"
                )

            response = blog_pb2.BlogResponse(
                id=blog.id,
                title=blog.title,
                slug=blog.slug or "",
                description=blog.description or "",
                content=blog.content or "",
                file_id=blog.file_id or 0,
                user_id=blog.user_id or 0,
                view_num=blog.view_num or 0,
                path_photo=self.get_photo_path(blog.file_id)
            )

            return self.add_category_and_tags(response, blog)

        except grpc.RpcError:
            db.rollback()
            raise

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    def CreateBlog(self, request, context):
        print("CreateBlog request received by gRPC server")

        if request.file_id:
            self.validate_file(request.file_id, context)

        db: Session = SessionLocal()

        try:
            input_slug = request.slug or request.title

            unique_slug = self.generate_unique_slug(
                db,
                input_slug
            )

            blog = Blog(
                title=request.title,
                slug=unique_slug,
                description=request.description,
                content=request.content,
                user_id=request.user_id,
                file_id=request.file_id or None
            )

            db.add(blog)
            db.commit()
            db.refresh(blog)

            blog = (
                db.query(Blog)
                .options(
                    selectinload(Blog.category),
                    selectinload(Blog.tags),
                )
                .filter(Blog.id == blog.id)
                .first()
            )

            response = blog_pb2.BlogResponse(
                id=blog.id,
                title=blog.title,
                slug=blog.slug or "",
                description=blog.description or "",
                content=blog.content or "",
                file_id=blog.file_id or 0,
                user_id=blog.user_id or 0,
                view_num=blog.view_num or 0,
                path_photo=self.get_photo_path(blog.file_id)
            )

            return self.add_category_and_tags(response, blog)

        except IntegrityError:
            db.rollback()
            context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                "A blog with this slug or another unique field already exists"
            )

        except grpc.RpcError:
            db.rollback()
            raise

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    def UpdateBlog(self, request, context):
        print("UpdateBlog request received by gRPC server")

        if request.file_id:
            self.validate_file(request.file_id, context)

        db: Session = SessionLocal()

        try:
            blog = db.query(Blog).filter(
                Blog.id == request.blog_id
            ).first()

            if not blog:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Blog not found"
                )

            new_slug = self.slugify(request.slug)

            if new_slug and new_slug != blog.slug:
                new_slug = self.generate_unique_slug(
                    db,
                    new_slug
                )
                blog.slug = new_slug

            blog.title = request.title
            blog.description = request.description
            blog.content = request.content
            blog.file_id = request.file_id or None

            db.commit()

            blog = (
                db.query(Blog)
                .options(
                    selectinload(Blog.category),
                    selectinload(Blog.tags),
                )
                .filter(Blog.id == request.blog_id)
                .first()
            )

            response = blog_pb2.BlogResponse(
                id=blog.id,
                title=blog.title,
                slug=blog.slug or "",
                description=blog.description or "",
                content=blog.content or "",
                file_id=blog.file_id or 0,
                user_id=blog.user_id or 0,
                view_num=blog.view_num or 0,
                path_photo=self.get_photo_path(blog.file_id)
            )

            return self.add_category_and_tags(response, blog)

        except IntegrityError:
            db.rollback()
            context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                "A blog with this slug or another unique field already exists"
            )

        except grpc.RpcError:
            db.rollback()
            raise

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    def DeleteBlog(self, request, context):
        print("DeleteBlog request received by gRPC server")
        db: Session = SessionLocal()

        try:
            blog = (
                db.query(Blog)
                .options(
                    selectinload(Blog.category),
                    selectinload(Blog.tags),
                )
                .filter(Blog.id == request.blog_id)
                .first()
            )

            if not blog:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Blog not found"
                )

            response = blog_pb2.BlogResponse(
                id=blog.id,
                title=blog.title,
                slug=blog.slug or "",
                description=blog.description or "",
                content=blog.content or "",
                file_id=blog.file_id or 0,
                user_id=blog.user_id or 0,
                view_num=blog.view_num or 0,
                path_photo=self.get_photo_path(blog.file_id)
            )

            self.add_category_and_tags(response, blog)

            db.delete(blog)
            db.commit()

            return response

        except grpc.RpcError:
            db.rollback()
            raise

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    blog_pb2_grpc.add_BlogServiceServicer_to_server(
        BlogService(), server
    )

    port = server.add_insecure_port("[::]:5053")

    if port == 0:
        raise RuntimeError("Could not bind to port 5053")

    server.start()
    print("Blog gRPC Server running on port 5053")

    try:
        server.wait_for_termination()

    except KeyboardInterrupt:
        server.stop(grace=2)


if __name__ == "__main__":
    serve()
