
from pathlib import Path
import sys

PROJECT_ROOT = Path(r"C:\Users\lotus\project")
GRPC_CATEGORY_DIR = PROJECT_ROOT / "grpc" / "category"

if str(GRPC_CATEGORY_DIR) not in sys.path:
    sys.path.insert(0, str(GRPC_CATEGORY_DIR))

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import grpc
from fastapi import FastAPI, HTTPException, Request
from fastapi.openapi.utils import get_openapi
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from google.protobuf.json_format import MessageToDict
from grpc import RpcError
from scalar_fastapi import get_scalar_api_reference

import category_pb2
import category_pb2_grpc


app = FastAPI(
    title="Category gRPC Gateway API",
    description="HTTP Gateway for Category gRPC Service",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url="/openapi.json",
)


# OpenAPI Bearer Token
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


channel = grpc.insecure_channel("localhost:5057")
stub = category_pb2_grpc.CategoryServiceStub(channel)


class CreateCategoryRequest(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Category name is required")

        return value


class UpdateCategoryRequest(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Category name is required")

        return value


# 422 Validation Error Handler
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = []

    for error in exc.errors():
        field = ".".join(str(item) for item in error["loc"])
        message = str(error["msg"])
        error_type = str(error["type"])

        errors.append({
            "field": field,
            "message": message,
            "type": error_type,
        })

    return JSONResponse(
        status_code=422,
        content={"detail": errors},
    )


def get_grpc_metadata(request: Request):
    authorization = request.headers.get("Authorization", "").strip()

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is missing",
        )

    parts = authorization.split(None, 1)

    if (
        len(parts) != 2
        or parts[0].lower() != "bearer"
        or not parts[1].strip()
    ):
        raise HTTPException(
            status_code=401,
            detail="Authorization must use Bearer token",
        )

    token = parts[1].strip()

    return (("authorization", f"Bearer {token}"),)


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
        grpc.StatusCode.RESOURCE_EXHAUSTED: 429,
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


@app.get("/scalar", include_in_schema=False)
def scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )


@app.get("/categories/")
def get_categories(request: Request):
    metadata = get_grpc_metadata(request)

    try:
        response = stub.GetCategories(
            category_pb2.Empty(),
            metadata=metadata,
            timeout=30,
        )

        return MessageToDict(
            response,
            preserving_proto_field_name=True,
        )

    except RpcError as exc:
        handle_grpc_error(exc)


@app.get("/categories/{category_id}")
def get_category(category_id: int, request: Request):
    metadata = get_grpc_metadata(request)

    if category_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="category_id must be greater than zero",
        )

    try:
        response = stub.GetCategory(
            category_pb2.CategoryRequest(
                category_id=category_id,
            ),
            metadata=metadata,
            timeout=30,
        )

        return MessageToDict(
            response,
            preserving_proto_field_name=True,
        )

    except RpcError as exc:
        handle_grpc_error(exc)


@app.post("/categories/", status_code=201)
def create_category(
    data: CreateCategoryRequest,
    request: Request,
):
    metadata = get_grpc_metadata(request)

    try:
        grpc_request = category_pb2.CreateCategoryRequest(
            name=data.name,
        )

        response = stub.CreateCategory(
            grpc_request,
            metadata=metadata,
            timeout=30,
        )

        return MessageToDict(
            response,
            preserving_proto_field_name=True,
        )

    except RpcError as exc:
        handle_grpc_error(exc)


@app.patch("/categories/{category_id}")
def update_category(
    category_id: int,
    data: UpdateCategoryRequest,
    request: Request,
):
    metadata = get_grpc_metadata(request)

    if category_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="category_id must be greater than zero",
        )

    try:
        grpc_request = category_pb2.UpdateCategoryRequest(
            category_id=category_id,
            name=data.name,
        )

        response = stub.UpdateCategory(
            grpc_request,
            metadata=metadata,
            timeout=30,
        )

        return MessageToDict(
            response,
            preserving_proto_field_name=True,
        )

    except RpcError as exc:
        handle_grpc_error(exc)


@app.delete("/categories/{category_id}")
def delete_category(category_id: int, request: Request):
    metadata = get_grpc_metadata(request)

    if category_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="category_id must be greater than zero",
        )

    try:
        grpc_request = category_pb2.DeleteCategoryRequest(
            category_id=category_id,
        )

        response = stub.DeleteCategory(
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
