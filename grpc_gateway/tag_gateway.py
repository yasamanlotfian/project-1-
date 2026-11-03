
from pathlib import Path
import sys

PROJECT_ROOT = Path(r"C:\Users\lotus\project")
GRPC_TAG_DIR = PROJECT_ROOT / "grpc" / "tag"

if str(GRPC_TAG_DIR) not in sys.path:
    sys.path.insert(0, str(GRPC_TAG_DIR))

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import grpc
from fastapi import FastAPI, HTTPException, Request
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from google.protobuf.json_format import MessageToDict
from grpc import RpcError
from scalar_fastapi import get_scalar_api_reference

import tag_pb2
import tag_pb2_grpc


app = FastAPI(
    title="Tag gRPC Gateway API",
    description="HTTP Gateway for Tag gRPC Service",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url="/openapi.json",
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


channel = grpc.insecure_channel("localhost:5056")
stub = tag_pb2_grpc.TagServiceStub(channel)



class CreateTagRequest(BaseModel):
    name: str


class UpdateTagRequest(BaseModel):
    name: str


def get_grpc_metadata(request: Request):
    authorization = request.headers.get("Authorization")

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is missing",
        )

    if not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization must use Bearer token",
        )

    return (("authorization", authorization),)



def handle_grpc_error(exc: RpcError):
    code = exc.code()
    details = exc.details()

    if code == grpc.StatusCode.UNAUTHENTICATED:
        raise HTTPException(
            status_code=401,
            detail=details or "Invalid or expired token",
        )

    if code == grpc.StatusCode.PERMISSION_DENIED:
        raise HTTPException(
            status_code=403,
            detail=details or "Permission denied",
        )

    if code == grpc.StatusCode.NOT_FOUND:
        raise HTTPException(
            status_code=404,
            detail=details or "Resource not found",
        )

    raise HTTPException(
        status_code=502,
        detail={
            "grpc_code": code.name if code else "UNKNOWN",
            "message": details or "gRPC service error",
        },
    )



@app.get("/scalar", include_in_schema=False)
def scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )



@app.get("/tags/")
def get_tags(request: Request):
    metadata = get_grpc_metadata(request)

    try:
        response = stub.GetTags(
            tag_pb2.Empty(),
            metadata=metadata,
            timeout=10,
        )

        return MessageToDict(
            response,
            preserving_proto_field_name=True,
        )

    except RpcError as exc:
        handle_grpc_error(exc)



@app.get("/tags/{tag_id}")
def get_tag(tag_id: int, request: Request):
    metadata = get_grpc_metadata(request)

    try:
        response = stub.GetTag(
            tag_pb2.TagRequest(tag_id=tag_id),
            metadata=metadata,
            timeout=10,
        )

        return MessageToDict(
            response,
            preserving_proto_field_name=True,
        )

    except RpcError as exc:
        handle_grpc_error(exc)



@app.post("/tags/", status_code=201)
def create_tag(data: CreateTagRequest, request: Request):
    metadata = get_grpc_metadata(request)

    try:
        grpc_request = tag_pb2.CreateTagRequest(
            name=data.name,
        )

        response = stub.CreateTag(
            grpc_request,
            metadata=metadata,
            timeout=10,
        )

        return MessageToDict(
            response,
            preserving_proto_field_name=True,
        )

    except RpcError as exc:
        handle_grpc_error(exc)



@app.patch("/tags/{tag_id}")
def update_tag(
    tag_id: int,
    data: UpdateTagRequest,
    request: Request,
):
    metadata = get_grpc_metadata(request)

    try:
        grpc_request = tag_pb2.UpdateTagRequest(
            tag_id=tag_id,
            name=data.name,
        )

        response = stub.UpdateTag(
            grpc_request,
            metadata=metadata,
            timeout=10,
        )

        return MessageToDict(
            response,
            preserving_proto_field_name=True,
        )

    except RpcError as exc:
        handle_grpc_error(exc)



@app.delete("/tags/{tag_id}")
def delete_tag(tag_id: int, request: Request):
    metadata = get_grpc_metadata(request)

    try:
        grpc_request = tag_pb2.DeleteTagRequest(
            tag_id=tag_id,
        )

        response = stub.DeleteTag(
            grpc_request,
            metadata=metadata,
            timeout=10,
        )

        return MessageToDict(
            response,
            preserving_proto_field_name=True,
        )

    except RpcError as exc:
        handle_grpc_error(exc)



@app.post("/tags/by-ids")
def get_tags_by_ids(ids: list[int], request: Request):
    metadata = get_grpc_metadata(request)

    try:
        grpc_request = tag_pb2.GetTagsByIdsRequest(
            ids=ids,
        )

        response = stub.GetTagsByIds(
            grpc_request,
            metadata=metadata,
            timeout=10,
        )

        return MessageToDict(
            response,
            preserving_proto_field_name=True,
        )

    except RpcError as exc:
        handle_grpc_error(exc)
