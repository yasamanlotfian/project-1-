
import sys
from concurrent import futures
from pathlib import Path

import grpc


PROJECT_ROOT = Path(__file__).resolve().parents[2]

for service_name in ("blog", "user"):
    service_path = PROJECT_ROOT / "grpc" / service_name

    if str(service_path) not in sys.path:
        sys.path.insert(0, str(service_path))

aggregation_path = PROJECT_ROOT / "grpc" / "aggregation"

if str(aggregation_path) not in sys.path:
    sys.path.insert(0, str(aggregation_path))


import blog_pb2
import blog_pb2_grpc

import user_pb2
import user_pb2_grpc

import aggregation_pb2
import aggregation_pb2_grpc


BLOG_ADDRESS = "localhost:5053"
USER_ADDRESS = "localhost:5051"

AGGREGATION_PORT = 5058


class AggregationService(
    aggregation_pb2_grpc.AggregationServiceServicer
):

    # تبدیل اطلاعات Blog به BlogData
    def blog_to_data(self, blog):
        return aggregation_pb2.BlogData(
            id=blog.id,
            title=blog.title,
            slug=blog.slug,
            description=blog.description,
            content=blog.content,
            user_id=blog.user_id,
            file_id=blog.file_id,
        )

    # دریافت اطلاعات کاربر از User Service
    def get_user(self, user_id):
        user_channel = grpc.insecure_channel(USER_ADDRESS)

        try:
            user_stub = user_pb2_grpc.UserServiceStub(
                user_channel
            )

            user = user_stub.GetUser(
                user_pb2.UserRequest(
                    user_id=user_id
                ),
                timeout=5,
            )

            return aggregation_pb2.UserData(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role,
            )

        finally:
            user_channel.close()

    # دریافت یک بلاگ همراه اطلاعات کاربر
    def GetAggregatedBlog(self, request, context):
        blog_channel = None

        try:
            blog_channel = grpc.insecure_channel(BLOG_ADDRESS)

            blog_stub = blog_pb2_grpc.BlogServiceStub(
                blog_channel
            )

            blog = blog_stub.GetBlog(
                blog_pb2.BlogRequest(
                    blog_id=request.blog_id
                ),
                timeout=5,
            )

            print("Blog ID:", blog.id)
            print("Blog User ID:", blog.user_id)

            user = self.get_user(blog.user_id)

            return aggregation_pb2.AggregatedBlogResponse(
                blog=self.blog_to_data(blog),
                user=user,
            )

        except grpc.RpcError as exc:
            print(
                "Aggregation error:",
                exc.code(),
                repr(exc.details()),
            )

            context.abort(
                exc.code(),
                exc.details() or "gRPC service request failed",
            )

        except Exception as exc:
            print("Unexpected Aggregation error:", repr(exc))

            context.abort(
                grpc.StatusCode.INTERNAL,
                "Unexpected error in Aggregation Service",
            )

        finally:
            if blog_channel is not None:
                blog_channel.close()

    # دریافت فهرست بلاگ‌ها
    def GetAggregatedBlogs(self, request, context):
        blog_channel = None

        try:
            blog_channel = grpc.insecure_channel(BLOG_ADDRESS)

            blog_stub = blog_pb2_grpc.BlogServiceStub(
                blog_channel
            )

            response = blog_stub.GetBlogs(
                blog_pb2.Empty(),
                timeout=5,
            )

            return aggregation_pb2.GetAggregatedBlogsResponse(
                blogs=[
                    self.blog_to_data(blog)
                    for blog in response.blogs
                ]
            )

        except grpc.RpcError as exc:
            print(
                "Get blogs error:",
                exc.code(),
                repr(exc.details()),
            )

            context.abort(
                exc.code(),
                exc.details() or "Could not get blogs",
            )

        except Exception as exc:
            print("Unexpected error:", repr(exc))

            context.abort(
                grpc.StatusCode.INTERNAL,
                "Unexpected error in Aggregation Service",
            )

        finally:
            if blog_channel is not None:
                blog_channel.close()

    # ایجاد بلاگ
    def CreateAggregatedBlog(self, request, context):
        blog_channel = None

        try:
            blog_channel = grpc.insecure_channel(BLOG_ADDRESS)

            blog_stub = blog_pb2_grpc.BlogServiceStub(
                blog_channel
            )

            file_id = (
                request.file_id
                if request.HasField("file_id")
                else 0
            )

            blog = blog_stub.CreateBlog(
                blog_pb2.CreateBlogRequest(
                    title=request.title,
                    slug=request.slug,
                    description=request.description,
                    content=request.content,
                    user_id=request.user_id,
                    file_id=file_id,
                ),
                timeout=5,
            )

            return aggregation_pb2.CreateAggregatedBlogResponse(
                blog=self.blog_to_data(blog)
            )

        except grpc.RpcError as exc:
            print(
                "Create blog error:",
                exc.code(),
                repr(exc.details()),
            )

            context.abort(
                exc.code(),
                exc.details() or "Could not create blog",
            )

        except Exception as exc:
            print("Unexpected error:", repr(exc))

            context.abort(
                grpc.StatusCode.INTERNAL,
                "Unexpected error in Aggregation Service",
            )

        finally:
            if blog_channel is not None:
                blog_channel.close()

    # ویرایش بلاگ
    def UpdateAggregatedBlog(self, request, context):
        blog_channel = None

        try:
            blog_channel = grpc.insecure_channel(BLOG_ADDRESS)

            blog_stub = blog_pb2_grpc.BlogServiceStub(
                blog_channel
            )

            # ابتدا اطلاعات فعلی بلاگ را دریافت می‌کنیم
            current_blog = blog_stub.GetBlog(
                blog_pb2.BlogRequest(
                    blog_id=request.blog_id
                ),
                timeout=5,
            )

            # BlogService در UpdateBlog امکان تغییر user_id ندارد
            if (
                request.HasField("user_id")
                and request.user_id != current_blog.user_id
            ):
                context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT,
                    "Changing user_id is not supported by BlogService",
                )

            # فقط فیلدهایی که ارسال شده‌اند تغییر می‌کنند
            title = (
                request.title
                if request.HasField("title")
                else current_blog.title
            )

            slug = (
                request.slug
                if request.HasField("slug")
                else current_blog.slug
            )

            description = (
                request.description
                if request.HasField("description")
                else current_blog.description
            )

            content = (
                request.content
                if request.HasField("content")
                else current_blog.content
            )

            file_id = (
                request.file_id
                if request.HasField("file_id")
                else current_blog.file_id
            )

            blog = blog_stub.UpdateBlog(
                blog_pb2.UpdateBlogRequest(
                    blog_id=request.blog_id,
                    title=title,
                    slug=slug,
                    description=description,
                    content=content,
                    file_id=file_id,
                ),
                timeout=5,
            )

            return aggregation_pb2.UpdateAggregatedBlogResponse(
                blog=self.blog_to_data(blog)
            )

        except grpc.RpcError as exc:
            print(
                "Update blog error:",
                exc.code(),
                repr(exc.details()),
            )

            context.abort(
                exc.code(),
                exc.details() or "Could not update blog",
            )

        except Exception as exc:
            print("Unexpected error:", repr(exc))

            context.abort(
                grpc.StatusCode.INTERNAL,
                "Unexpected error in Aggregation Service",
            )

        finally:
            if blog_channel is not None:
                blog_channel.close()

    # حذف بلاگ
    def DeleteAggregatedBlog(self, request, context):
        blog_channel = None

        try:
            blog_channel = grpc.insecure_channel(BLOG_ADDRESS)

            blog_stub = blog_pb2_grpc.BlogServiceStub(
                blog_channel
            )

            blog_stub.DeleteBlog(
                blog_pb2.DeleteBlogRequest(
                    blog_id=request.blog_id
                ),
                timeout=5,
            )

            return aggregation_pb2.DeleteAggregatedBlogResponse(
                success=True,
                message="Blog deleted successfully",
            )

        except grpc.RpcError as exc:
            print(
                "Delete blog error:",
                exc.code(),
                repr(exc.details()),
            )

            context.abort(
                exc.code(),
                exc.details() or "Could not delete blog",
            )

        except Exception as exc:
            print("Unexpected error:", repr(exc))

            context.abort(
                grpc.StatusCode.INTERNAL,
                "Unexpected error in Aggregation Service",
            )

        finally:
            if blog_channel is not None:
                blog_channel.close()


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    aggregation_pb2_grpc.add_AggregationServiceServicer_to_server(
        AggregationService(),
        server,
    )

    port = server.add_insecure_port(
        f"[::]:{AGGREGATION_PORT}"
    )

    if port == 0:
        raise RuntimeError(
            f"Could not bind to port {AGGREGATION_PORT}"
        )

    server.start()

    print(
        f"Aggregation gRPC Server running on port "
        f"{AGGREGATION_PORT}"
    )

    try:
        server.wait_for_termination()

    except KeyboardInterrupt:
        server.stop(grace=2)


if __name__ == "__main__":
    serve()
