
import sys
from pathlib import Path

import grpc


PROJECT_ROOT = Path(__file__).resolve().parents[2]

aggregation_path = PROJECT_ROOT / "grpc" / "aggregation"

if str(aggregation_path) not in sys.path:
    sys.path.insert(0, str(aggregation_path))


import aggregation_pb2
import aggregation_pb2_grpc


AGGREGATION_ADDRESS = "localhost:5058"


def run():
    with grpc.insecure_channel(AGGREGATION_ADDRESS) as channel:
        stub = aggregation_pb2_grpc.AggregationServiceStub(channel)

        response = stub.GetAggregatedBlog(
            aggregation_pb2.AggregatedBlogRequest(blog_id=1),
            timeout=15,
        )

        print("Blog Information:")
        print(f"ID: {response.blog.id}")
        print(f"Title: {response.blog.title}")
        print(f"Slug: {response.blog.slug}")
        print(f"Description: {response.blog.description}")
        print(f"Content: {response.blog.content}")
        print(f"User ID: {response.blog.user_id}")
        print(f"File ID: {response.blog.file_id}")

        print("\nUser Information:")
        print(f"ID: {response.user.id}")
        print(f"Username: {response.user.username}")
        print(f"Email: {response.user.email}")
        print(f"Role: {response.user.role}")


if __name__ == "__main__":
    try:
        run()

    except grpc.RpcError as exc:
        print(f"gRPC Error: {exc.code()}")
        print(f"Details: {exc.details()}")
