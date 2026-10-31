
import sys
from concurrent import futures

import grpc
from sqlalchemy.orm import Session

sys.path.insert(0, r"C:\Users\lotus\project")
sys.path.insert(0, r"C:\Users\lotus\project\grpc\comment")

from database import SessionLocal
from tables.comment import Comment
from tables.blog import Blog

import comment_pb2
import comment_pb2_grpc


class CommentService(comment_pb2_grpc.CommentServiceServicer):

    def GetComments(self, request, context):
        db: Session = SessionLocal()

        try:
            comments = db.query(Comment).all()
            response = comment_pb2.CommentList()

            for comment in comments:
                response.comments.add(
                    id=comment.id,
                    name=comment.name,
                    blog_id=comment.blog_id,
                    content=comment.content or "",
                    created_at=(
                        comment.created_at.isoformat()
                        if comment.created_at
                        else ""
                    )
                )

            return response
        finally:
            db.close()

    def GetComment(self, request, context):
        db: Session = SessionLocal()

        try:
            comment = (
                db.query(Comment)
                .filter(Comment.id == request.comment_id)
                .first()
            )

            if not comment:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Comment not found")
                return comment_pb2.CommentResponse()

            return comment_pb2.CommentResponse(
                id=comment.id,
                name=comment.name,
                blog_id=comment.blog_id,
                content=comment.content or "",
                created_at=(
                    comment.created_at.isoformat()
                    if comment.created_at
                    else ""
                )
            )
        finally:
            db.close()

    def CreateComment(self, request, context):
        db: Session = SessionLocal()

        try:
            blog = (
                db.query(Blog)
                .filter(Blog.id == request.blog_id)
                .first()
            )

            if not blog:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Blog not found")
                return comment_pb2.CommentResponse()

            comment = Comment(
                name=request.name,
                blog_id=request.blog_id,
                content=request.content
            )

            db.add(comment)
            db.commit()
            db.refresh(comment)

            return comment_pb2.CommentResponse(
                id=comment.id,
                name=comment.name,
                blog_id=comment.blog_id,
                content=comment.content or "",
                created_at=(
                    comment.created_at.isoformat()
                    if comment.created_at
                    else ""
                )
            )
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def UpdateComment(self, request, context):
        db: Session = SessionLocal()

        try:
            comment = (
                db.query(Comment)
                .filter(Comment.id == request.comment_id)
                .first()
            )

            if not comment:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Comment not found")
                return comment_pb2.CommentResponse()

            comment.name = request.name
            comment.content = request.content

            db.commit()
            db.refresh(comment)

            return comment_pb2.CommentResponse(
                id=comment.id,
                name=comment.name,
                blog_id=comment.blog_id,
                content=comment.content or "",
                created_at=(
                    comment.created_at.isoformat()
                    if comment.created_at
                    else ""
                )
            )
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def DeleteComment(self, request, context):
        db: Session = SessionLocal()

        try:
            comment = (
                db.query(Comment)
                .filter(Comment.id == request.comment_id)
                .first()
            )

            if not comment:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Comment not found")
                return comment_pb2.CommentResponse()

            response = comment_pb2.CommentResponse(
                id=comment.id,
                name=comment.name,
                blog_id=comment.blog_id,
                content=comment.content or "",
                created_at=(
                    comment.created_at.isoformat()
                    if comment.created_at
                    else ""
                )
            )

            db.delete(comment)
            db.commit()

            return response
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    comment_pb2_grpc.add_CommentServiceServicer_to_server(
        CommentService(),
        server
    )

    server.add_insecure_port("[::]:5054")
    server.start()

    print("Comment gRPC Server running on port 5054")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
