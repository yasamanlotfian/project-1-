
from pathlib import Path
import sys

PROJECT_ROOT = Path(r"C:\Users\lotus\project")
GRPC_BLOG_DIR = PROJECT_ROOT / "grpc" / "blog"

if str(GRPC_BLOG_DIR) not in sys.path:
    sys.path.insert(0, str(GRPC_BLOG_DIR))

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import grpc
from fastapi import FastAPI, HTTPException, Request
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field
from google.protobuf.json_format import MessageToDict
from grpc import RpcError
from scalar_fastapi import get_scalar_api_reference

import blog_pb2
import blog_pb2_grpc


app = FastAPI(
    title="Blog gRPC Gateway API",
    description="HTTP Gateway for Blog gRPC Service",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url="/openapi.json"
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    schema.setdefault("components", {}).setdefault(
        "securitySchemes", {}
    )["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }

    schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi


channel = grpc.insecure_channel("localhost:5053")
stub = blog_pb2_grpc.BlogServiceStub(channel)


class CreateBlogRequest(BaseModel):
    title: str
    slug: str
    description: str = ""
    content: str = ""
    user_id: int
    file_id: int | None = None
    category_id: int
    tag_ids: list[int] = Field(default_factory=list)


class UpdateBlogRequest(BaseModel):
    title: str
    slug: str
    description: str = ""
    content: str = ""
    file_id: int | None = None


def get_grpc_metadata(request: Request):
    authorization = request.headers.get("Authorization")

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is missing"
        )

    if not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization must use Bearer token"
        )

    return (("authorization", authorization),)


def handle_grpc_error(exc: RpcError):
    code = exc.code()
    details = exc.details()

    if code == grpc.StatusCode.UNAUTHENTICATED:
        raise HTTPException(
            status_code=401,
            detail=details or "Invalid or expired token"
        )

    if code == grpc.StatusCode.PERMISSION_DENIED:
        raise HTTPException(
            status_code=403,
            detail=details or "Permission denied"
        )

    if code == grpc.StatusCode.NOT_FOUND:
        raise HTTPException(
            status_code=404,
            detail=details or "Resource not found"
        )

    raise HTTPException(
        status_code=502,
        detail={
            "grpc_code": code.name if code else "UNKNOWN",
            "message": details or "gRPC service error"
        }
    )


def convert_blog_response(response):
    result = MessageToDict(
        response,
        preserving_proto_field_name=True
    )

    result.setdefault("view_num", 0)
    result.setdefault("path_photo", "")

  
    result.setdefault("category", None)

    result.setdefault("tags", [])

    return result


@app.get("/scalar", include_in_schema=False)
def scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title
    )


@app.get("/blogs/")
def get_blogs(request: Request):
    metadata = get_grpc_metadata(request)

    try:
        response = stub.GetBlogs(
            blog_pb2.Empty(),
            metadata=metadata,
            timeout=10
        )

        return {
            "blogs": [
                convert_blog_response(blog)
                for blog in response.blogs
            ]
        }

    except RpcError as exc:
        handle_grpc_error(exc)


@app.get("/blogs/{blog_id}")
def get_blog(blog_id: int, request: Request):
    metadata = get_grpc_metadata(request)

    try:
        response = stub.GetBlog(
            blog_pb2.BlogRequest(blog_id=blog_id),
            metadata=metadata,
            timeout=10
        )

        return convert_blog_response(response)

    except RpcError as exc:
        handle_grpc_error(exc)


@app.post("/blogs/", status_code=201)
def create_blog(data: CreateBlogRequest, request: Request):
    metadata = get_grpc_metadata(request)

    try:
        grpc_request = blog_pb2.CreateBlogRequest(
            title=data.title,
            slug=data.slug,
            description=data.description,
            content=data.content,
            user_id=data.user_id,
            file_id=data.file_id or 0,
            category_id=data.category_id,
            tag_ids=data.tag_ids

        )

        response = stub.CreateBlog(
            grpc_request,
            metadata=metadata,
            timeout=10
        )

        return convert_blog_response(response)

    except RpcError as exc:
        handle_grpc_error(exc)


@app.patch("/blogs/{blog_id}")
def update_blog(
    blog_id: int,
    data: UpdateBlogRequest,
    request: Request
):
    metadata = get_grpc_metadata(request)

    try:
        grpc_request = blog_pb2.UpdateBlogRequest(
            blog_id=blog_id,
            title=data.title,
            slug=data.slug,
            description=data.description,
            content=data.content,
            file_id=data.file_id or 0
        )

        response = stub.UpdateBlog(
            grpc_request,
            metadata=metadata,
            timeout=10
        )

        return convert_blog_response(response)

    except RpcError as exc:
        handle_grpc_error(exc)


@app.delete("/blogs/{blog_id}")
def delete_blog(blog_id: int, request: Request):
    metadata = get_grpc_metadata(request)

    try:
        response = stub.DeleteBlog(
            blog_pb2.DeleteBlogRequest(blog_id=blog_id),
            metadata=metadata,
            timeout=10
        )

        return convert_blog_response(response)

    except RpcError as exc:
        handle_grpc_error(exc)
