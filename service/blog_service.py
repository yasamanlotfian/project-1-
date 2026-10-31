
import sys
from pathlib import Path

import grpc

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BLOG_GRPC_DIR = PROJECT_ROOT / "grpc" / "blog"

if str(BLOG_GRPC_DIR) not in sys.path:
    sys.path.insert(0, str(BLOG_GRPC_DIR))

import blog_pb2
import blog_pb2_grpc


class BlogServiceClient:

    def __init__(self, address="localhost:5053"):
        self.channel = grpc.insecure_channel(address)
        self.stub = blog_pb2_grpc.BlogServiceStub(self.channel)

    def get_blogs(self, metadata=None):
        return self.stub.GetBlogs(
            blog_pb2.Empty(),
            metadata=metadata,
            timeout=30
        )

    def get_blog(self, blog_id: int, metadata=None):
        return self.stub.GetBlog(
            blog_pb2.BlogRequest(blog_id=blog_id),
            metadata=metadata,
            timeout=10
        )

    def create_blog(
        self, title, slug, description, content, user_id,   file_id,
        metadata=None
    ):
        request = blog_pb2.CreateBlogRequest(
            title=title,
            slug=slug,
            description=description,
            content=content,
            user_id=user_id,
            file_id=file_id
        )
        return self.stub.CreateBlog(
            request,
            metadata=metadata,
            timeout=10
        )

    def update_blog(
        self,
        blog_id: int,
        title: str,
        slug: str,
        description: str,
        content: str,
        metadata=None
    ):
        request = blog_pb2.UpdateBlogRequest(
            blog_id=blog_id,
            title=title,
            slug=slug,
            description=description,
            content=content
        )
        return self.stub.UpdateBlog(
            request,
            metadata=metadata,
            timeout=10
        )

    def delete_blog(self, blog_id: int, metadata=None):
        request = blog_pb2.DeleteBlogRequest(
            blog_id=blog_id
        )
        return self.stub.DeleteBlog(
            request,
            metadata=metadata,
            timeout=10
        )

    def close(self):
        self.channel.close()
