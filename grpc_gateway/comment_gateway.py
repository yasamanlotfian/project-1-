
from pathlib import Path
import sys

PROJECT_ROOT = Path(r"C:\Users\lotus\project")
GRPC_COMMENT_DIR = PROJECT_ROOT / "grpc" / "comment"

sys.path.insert(0, str(GRPC_COMMENT_DIR))
sys.path.insert(0, str(PROJECT_ROOT))

import grpc
from fastapi import FastAPI, HTTPException, Request
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from google.protobuf.json_format import MessageToDict
from grpc import RpcError
from scalar_fastapi import get_scalar_api_reference

import comment_pb2
import comment_pb2_grpc


app = FastAPI(
    title="Comment gRPC Gateway API",
    description="HTTP Gateway for Comment gRPC Service",
    version="1.0.0"
)

channel = grpc.insecure_channel("localhost:5054")
stub = comment_pb2_grpc.CommentServiceStub(channel)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema.setdefault("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    for path_item in openapi_schema["paths"].values():
        for operation in path_item.values():
            if isinstance(operation, dict) and "responses" in operation:
                operation["security"] = [
                    {"BearerAuth": []}
                ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


class CreateCommentRequest(BaseModel):
    name: str
    blog_id: int
    content: str


class UpdateCommentRequest(BaseModel):
    name: str
    content: str


# Receive JWT from Authorization header
def get_grpc_metadata(request: Request):
    authorization = request.headers.get("Authorization")

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Bearer token"
        )

    token = authorization[7:].strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Bearer token"
        )

    return (("authorization", f"Bearer {token}"),)


def handle_grpc_error(exc: RpcError):
    code = exc.code()
    details = exc.details() or "gRPC request failed"

    if code == grpc.StatusCode.NOT_FOUND:
        raise HTTPException(status_code=404, detail=details)

    if code == grpc.StatusCode.ALREADY_EXISTS:
        raise HTTPException(status_code=409, detail=details)

    if code == grpc.StatusCode.INVALID_ARGUMENT:
        raise HTTPException(status_code=400, detail=details)

    if code == grpc.StatusCode.UNAUTHENTICATED:
        raise HTTPException(status_code=401, detail=details)

    if code == grpc.StatusCode.PERMISSION_DENIED:
        raise HTTPException(status_code=403, detail=details)

    raise HTTPException(
        status_code=502,
        detail={
            "grpc_code": code.name if code else "UNKNOWN",
            "message": details
        }
    )


@app.get("/scalar", include_in_schema=False)
def scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title
    )


@app.get("/comments/")
def get_comments(request: Request):
    metadata = get_grpc_metadata(request)

    try:
        response = stub.GetComments(
            comment_pb2.Empty(),
            metadata=metadata,
            timeout=5
        )

        return MessageToDict(
            response,
            preserving_proto_field_name=True
        )

    except RpcError as exc:
        handle_grpc_error(exc)


@app.get("/comments/{comment_id}")
def get_comment(comment_id: int, request: Request):
    metadata = get_grpc_metadata(request)

    try:
        response = stub.GetComment(
            comment_pb2.CommentRequest(
                comment_id=comment_id
            ),
            metadata=metadata,
            timeout=5
        )

        return MessageToDict(
            response,
            preserving_proto_field_name=True
        )

    except RpcError as exc:
        handle_grpc_error(exc)


@app.post("/comments/", status_code=201)
def create_comment(
    data: CreateCommentRequest,
    request: Request
):
    metadata = get_grpc_metadata(request)

    try:
        grpc_request = comment_pb2.CreateCommentRequest(
            name=data.name,
            blog_id=data.blog_id,
            content=data.content
        )

        response = stub.CreateComment(
            grpc_request,
            metadata=metadata,
            timeout=5
        )

        return MessageToDict(
            response,
            preserving_proto_field_name=True
        )

    except RpcError as exc:
        handle_grpc_error(exc)


@app.patch("/comments/{comment_id}")
def update_comment(
    comment_id: int,
    data: UpdateCommentRequest,
    request: Request
):
    metadata = get_grpc_metadata(request)

    try:
        grpc_request = comment_pb2.UpdateCommentRequest(
            comment_id=comment_id,
            name=data.name,
            content=data.content
        )

        response = stub.UpdateComment(
            grpc_request,
            metadata=metadata,
            timeout=5
        )

        return MessageToDict(
            response,
            preserving_proto_field_name=True
        )

    except RpcError as exc:
        handle_grpc_error(exc)


@app.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    request: Request
):
    metadata = get_grpc_metadata(request)

    try:
        response = stub.DeleteComment(
            comment_pb2.DeleteCommentRequest(
                comment_id=comment_id
            ),
            metadata=metadata,
            timeout=5
        )

        return MessageToDict(
            response,
            preserving_proto_field_name=True
        )

    except RpcError as exc:
        handle_grpc_error(exc)
