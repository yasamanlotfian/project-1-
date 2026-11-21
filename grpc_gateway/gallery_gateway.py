
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


class CreateGalleryRequest(BaseModel):

    title: str
    file_id: int


class UpdateGalleryRequest(BaseModel):

    title: str | None = None
    file_id: int | None = None




def get_grpc_metadata(request: Request):

    authorization = request.headers.get(
        "Authorization", ""
    ).strip()

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

    return (
        ("authorization", f"Bearer {parts[1]}"),
    )


def handle_grpc_error(exc: RpcError):

    code = exc.code()
    details = exc.details() or "gRPC service error"

    status_map = {
        grpc.StatusCode.UNAUTHENTICATED: 401,
        grpc.StatusCode.PERMISSION_DENIED: 403,
        grpc.StatusCode.NOT_FOUND: 404,
        grpc.StatusCode.INVALID_ARGUMENT: 400,
        grpc.StatusCode.ALREADY_EXISTS: 409,
        grpc.StatusCode.FAILED_PRECONDITION: 409,
        grpc.StatusCode.UNAVAILABLE: 503,
        grpc.StatusCode.DEADLINE_EXCEEDED: 504,
        grpc.StatusCode.INTERNAL: 500,
    }

    raise HTTPException(
        status_code=status_map.get(code, 502),
        detail={
            "grpc_code": code.name if code else "UNKNOWN",
            "message": details,
        },
    )



def message_to_dict(message):

    return MessageToDict(
        message,
        preserving_proto_field_name=True,
    )



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

        return message_to_dict(response)

    except RpcError as exc:
        handle_grpc_error(exc)




@app.get("/galleries/{gallery_id}")
def get_gallery(
    gallery_id: int,
    request: Request,
):

    metadata = get_grpc_metadata(request)

    try:
        grpc_request = gallery_pb2.GalleryRequest(
            gallery_id=gallery_id,
        )

        response = stub.GetGallery(
            grpc_request,
            metadata=metadata,
        )

        return message_to_dict(response)

    except RpcError as exc:
        handle_grpc_error(exc)




@app.post("/galleries/", status_code=201)
def create_gallery(
    data: CreateGalleryRequest,
    request: Request,
):

    metadata = get_grpc_metadata(request)

    if not data.title.strip():
        raise HTTPException(
            status_code=422,
            detail="Title cannot be empty",
        )

    try:
        grpc_request = gallery_pb2.CreateGalleryRequest(
            title=data.title.strip(),
            file_id=data.file_id,
        )

        response = stub.CreateGallery(
            grpc_request,
            metadata=metadata,
        )

        return message_to_dict(response)

    except RpcError as exc:
        handle_grpc_error(exc)



@app.patch("/galleries/{gallery_id}")
def update_gallery(
    gallery_id: int,
    data: UpdateGalleryRequest,
    request: Request,
):

    metadata = get_grpc_metadata(request)

    fields_set = getattr(
        data,
        "model_fields_set",
        None,
    )

    if fields_set is None:
        fields_set = getattr(
            data,
            "__fields_set__",
            set(),
        )

    if not fields_set:
        raise HTTPException(
            status_code=422,
            detail="At least one field must be provided",
        )

    if "title" in fields_set and data.title is None:
        raise HTTPException(
            status_code=422,
            detail="Title cannot be null",
        )

    if "file_id" in fields_set and data.file_id is None:
        raise HTTPException(
            status_code=422,
            detail="file_id cannot be null",
        )

    try:

      

        current_response = stub.GetGallery(
            gallery_pb2.GalleryRequest(
                gallery_id=gallery_id,
            ),
            metadata=metadata,
        )

        current = message_to_dict(current_response)

    

        title = (
            data.title
            if "title" in fields_set
            else current.get("title", "")
        )

        file_id = (
            data.file_id
            if "file_id" in fields_set
            else current.get("file_id", 0)
        )

   

        if not title or not title.strip():
            raise HTTPException(
                status_code=422,
                detail="Title cannot be empty",
            )

        if not file_id:
            raise HTTPException(
                status_code=422,
                detail="file_id is required",
            )

        # gRPC Request

        grpc_request = gallery_pb2.UpdateGalleryRequest(
            gallery_id=gallery_id,
            title=title.strip(),
            file_id=file_id,
        )

        response = stub.UpdateGallery(
            grpc_request,
            metadata=metadata,
        )

        return message_to_dict(response)

    except HTTPException:
        raise

    except RpcError as exc:
        handle_grpc_error(exc)



@app.delete("/galleries/{gallery_id}")
def delete_gallery(
    gallery_id: int,
    request: Request,
):

    metadata = get_grpc_metadata(request)

    try:
        grpc_request = gallery_pb2.DeleteGalleryRequest(
            gallery_id=gallery_id,
        )

        response = stub.DeleteGallery(
            grpc_request,
            metadata=metadata,
        )

        return message_to_dict(response)

    except RpcError as exc:
        handle_grpc_error(exc)
