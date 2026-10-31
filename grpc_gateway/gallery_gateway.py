
from pathlib import Path
import sys

PROJECT_ROOT = Path(r"C:\Users\lotus\project")
GRPC_GALLERY_DIR = PROJECT_ROOT / "grpc" / "gallery"

sys.path.insert(0, str(GRPC_GALLERY_DIR))
sys.path.insert(0, str(PROJECT_ROOT))

import grpc
from fastapi import FastAPI, HTTPException, Request
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from google.protobuf.json_format import MessageToDict
from grpc import RpcError
from scalar_fastapi import get_scalar_api_reference

from service.file_service import FileServiceClient

import gallery_pb2
import gallery_pb2_grpc


app = FastAPI(
    title="Gallery gRPC Gateway API",
    description="HTTP Gateway for Gallery gRPC Service",
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


channel = grpc.insecure_channel("localhost:5052")
stub = gallery_pb2_grpc.GalleryServiceStub(channel)

file_client = FileServiceClient(address="localhost:5055")


class CreateGalleryRequest(BaseModel):
    title: str
    file_id: int


class UpdateGalleryRequest(BaseModel):
    title: str


def get_grpc_metadata(request: Request):
    authorization = request.headers.get("Authorization", "").strip()

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is missing",
        )

    parts = authorization.split(None, 1)

    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Expected Authorization: Bearer <token>",
        )

    return (("authorization", f"Bearer {parts[1]}"),)


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
            detail=details or "Gallery not found",
        )

    raise HTTPException(
        status_code=502,
        detail={
            "grpc_code": code.name if code else "UNKNOWN",
            "message": details or "gRPC service error",
        },
    )


def add_file_urls(gallery_data: dict):
    file_id = gallery_data.get("file_id")

    if file_id is None:
        return gallery_data

    try:
        file_data = file_client.get_file(int(file_id))

        gallery_data["original_file_url"] = getattr(
            file_data, "original_file_url", ""
        )
        gallery_data["optimized_file_url"] = getattr(
            file_data, "optimized_file_url", ""
        )
        gallery_data["crop_file_url"] = getattr(
            file_data, "crop_file_url", ""
        )

        return gallery_data

    except RpcError as exc:
        handle_grpc_error(exc)


@app.get("/scalar", include_in_schema=False)
def scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )


@app.get("/galleries/")
def get_galleries(request: Request):
    metadata = get_grpc_metadata(request)

    try:
        response = stub.GetGalleries(
            gallery_pb2.Empty(),
            metadata=metadata,
        )

        result = MessageToDict(
            response,
            preserving_proto_field_name=True,
        )

        if "galleries" in result:
            result["galleries"] = [
                add_file_urls(gallery)
                for gallery in result["galleries"]
            ]

        return result

    except RpcError as exc:
        handle_grpc_error(exc)


@app.get("/galleries/{gallery_id}")
def get_gallery(gallery_id: int, request: Request):
    metadata = get_grpc_metadata(request)

    try:
        grpc_request = gallery_pb2.GalleryRequest(
            gallery_id=gallery_id,
        )

        response = stub.GetGallery(
            grpc_request,
            metadata=metadata,
        )

        result = MessageToDict(
            response,
            preserving_proto_field_name=True,
        )

        return add_file_urls(result)

    except RpcError as exc:
        handle_grpc_error(exc)


@app.post("/galleries/", status_code=201)
def create_gallery(data: CreateGalleryRequest, request: Request):
    metadata = get_grpc_metadata(request)

    try:
    
        file_client.get_file(data.file_id)

        grpc_request = gallery_pb2.CreateGalleryRequest(
            title=data.title,
            file_id=data.file_id,
        )

        response = stub.CreateGallery(
            grpc_request,
            metadata=metadata,
        )

        result = MessageToDict(
            response,
            preserving_proto_field_name=True,
        )

        return add_file_urls(result)

    except RpcError as exc:
        handle_grpc_error(exc)


@app.patch("/galleries/{gallery_id}")
def update_gallery(
    gallery_id: int,
    data: UpdateGalleryRequest,
    request: Request,
):
    metadata = get_grpc_metadata(request)

    try:
        grpc_request = gallery_pb2.UpdateGalleryRequest(
            gallery_id=gallery_id,
            title=data.title,
        )

        response = stub.UpdateGallery(
            grpc_request,
            metadata=metadata,
        )

        return MessageToDict(
            response,
            preserving_proto_field_name=True,
        )

    except RpcError as exc:
        handle_grpc_error(exc)


@app.delete("/galleries/{gallery_id}")
def delete_gallery(gallery_id: int, request: Request):
    metadata = get_grpc_metadata(request)

    try:
        grpc_request = gallery_pb2.DeleteGalleryRequest(
            gallery_id=gallery_id,
        )

        response = stub.DeleteGallery(
            grpc_request,
            metadata=metadata,
        )

        return MessageToDict(
            response,
            preserving_proto_field_name=True,
        )

    except RpcError as exc:
        handle_grpc_error(exc)
