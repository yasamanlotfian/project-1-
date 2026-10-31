
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

    def GetAggregatedBlog(self, request, context):
        blog_channel = None
        user_channel = None

        try:
            # دریافت اطلاعات Blog
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

            # دریافت اطلاعات User
            user_channel = grpc.insecure_channel(USER_ADDRESS)

            user_stub = user_pb2_grpc.UserServiceStub(
                user_channel
            )

            user = user_stub.GetUser(
                user_pb2.UserRequest(
                    user_id=blog.user_id
                ),
                timeout=5,
            )

            # برگرداندن پاسخ تجمیع‌شده
            return aggregation_pb2.AggregatedBlogResponse(
                blog=aggregation_pb2.BlogData(
                    id=blog.id,
                    title=blog.title,
                    slug=blog.slug,
                    description=blog.description,
                    content=blog.content,
                    user_id=blog.user_id,
                    file_id=blog.file_id,
                ),
                user=aggregation_pb2.UserData(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    role=user.role,
                ),
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

            if user_channel is not None:
                user_channel.close()


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
