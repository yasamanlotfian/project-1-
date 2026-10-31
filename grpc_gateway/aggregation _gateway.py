
import sys
from pathlib import Path

import grpc
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from scalar_fastapi import get_scalar_api_reference

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGGREGATION_PATH = PROJECT_ROOT / "grpc" / "aggregation"

if str(AGGREGATION_PATH) not in sys.path:
    sys.path.insert(0, str(AGGREGATION_PATH))

import aggregation_pb2
import aggregation_pb2_grpc


app = FastAPI(
    title="Aggregation API",
    description="Blog and User Aggregation using gRPC",
    version="1.0.0",
)


class AggregatedBlogCreate(BaseModel):
    title: str
    slug: str
    description: str = ""
    content: str = ""
    user_id: int
    file_id: int | None = None


class AggregatedBlogPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    slug: str | None = None
    description: str | None = None
    content: str | None = None
    user_id: int | None = None
    file_id: int | None = None


def get_aggregation_stub():
    channel = grpc.insecure_channel("localhost:5058")
    stub = aggregation_pb2_grpc.AggregationServiceStub(channel)
    return channel, stub


def grpc_error(exc: grpc.RpcError):
    raise HTTPException(
        status_code=502,
        detail={
            "grpc_code": exc.code().name,
            "message": exc.details(),
        },
    ) from exc


def blog_to_dict(blog):
    return {
        "id": blog.id,
        "title": blog.title,
        "slug": blog.slug,
        "description": blog.description,
        "content": blog.content,
        "user_id": blog.user_id,
        "file_id": blog.file_id,
    }


@app.get("/scalar", include_in_schema=False)
def scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Aggregation API Reference",
    )


@app.get("/aggregation/blogs")
def get_aggregated_blogs():
    channel, stub = get_aggregation_stub()

    try:
        response = stub.GetAggregatedBlogs(
            aggregation_pb2.Empty(),
            timeout=10,
        )

        return {
            "blogs": [
                blog_to_dict(blog)
                for blog in response.blogs
            ]
        }

    except grpc.RpcError as exc:
        grpc_error(exc)

    finally:
        channel.close()


@app.get("/aggregation/blogs/{blog_id}")
def get_aggregated_blog(blog_id: int):
    channel, stub = get_aggregation_stub()

    try:
        response = stub.GetAggregatedBlog(
            aggregation_pb2.AggregatedBlogRequest(
                blog_id=blog_id
            ),
            timeout=10,
        )

        return {
            "blog": blog_to_dict(response.blog),
            "user": {
                "id": response.user.id,
                "username": response.user.username,
                "email": response.user.email,
                "role": response.user.role,
            },
        }

    except grpc.RpcError as exc:
        grpc_error(exc)

    finally:
        channel.close()


@app.post("/aggregation/blogs", status_code=201)
def create_aggregated_blog(data: AggregatedBlogCreate):
    channel, stub = get_aggregation_stub()

    try:
        payload = data.model_dump(exclude_none=True)

        response = stub.CreateAggregatedBlog(
            aggregation_pb2.CreateAggregatedBlogRequest(
                **payload
            ),
            timeout=10,
        )

        return {
            "message": "Blog created successfully",
            "blog": blog_to_dict(response.blog),
        }

    except grpc.RpcError as exc:
        grpc_error(exc)

    finally:
        channel.close()


@app.patch("/aggregation/blogs/{blog_id}")
def update_aggregated_blog(
    blog_id: int,
    data: AggregatedBlogPatch,
):
    channel, stub = get_aggregation_stub()

    try:
        payload = data.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )

        if not payload:
            raise HTTPException(
                status_code=400,
                detail="At least one field must be provided",
            )

        response = stub.UpdateAggregatedBlog(
            aggregation_pb2.UpdateAggregatedBlogRequest(
                blog_id=blog_id,
                **payload,
            ),
            timeout=10,
        )

        return {
            "message": "Blog updated successfully",
            "blog": blog_to_dict(response.blog),
        }

    except grpc.RpcError as exc:
        grpc_error(exc)

    finally:
        channel.close()


@app.delete("/aggregation/blogs/{blog_id}")
def delete_aggregated_blog(blog_id: int):
    channel, stub = get_aggregation_stub()

    try:
        response = stub.DeleteAggregatedBlog(
            aggregation_pb2.DeleteAggregatedBlogRequest(
                blog_id=blog_id
            ),
            timeout=10,
        )

        return {
            "message": response.message,
            "success": response.success,
        }

    except grpc.RpcError as exc:
        grpc_error(exc)

    finally:
        channel.close()



