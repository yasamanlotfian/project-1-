
from pathlib import Path
import sys

PROJECT_ROOT = Path(r"C:\Users\lotus\project")
GRPC_USER_DIR = PROJECT_ROOT / "grpc" / "user"

sys.path.insert(0, str(GRPC_USER_DIR))
sys.path.insert(0, str(PROJECT_ROOT))

import grpc
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.protobuf.json_format import MessageToDict
from grpc import RpcError
from scalar_fastapi import get_scalar_api_reference

import user_pb2
import user_pb2_grpc


app = FastAPI(
    title="User gRPC Gateway API",
    description="HTTP Gateway for User gRPC Service",
    version="1.0.0"
)

channel = grpc.insecure_channel("localhost:5051")
stub = user_pb2_grpc.UserServiceStub(channel)


class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str


class UpdateUserRequest(BaseModel):
    username: str = ""
    email: str = ""
    password: str = ""
    role: str = ""


class LoginRequest(BaseModel):
    username: str
    password: str


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
        title="User gRPC Gateway API"
    )


@app.get("/users/")
def get_users():
    try:
        response = stub.GetUsers(user_pb2.Empty(), timeout=5)
        return MessageToDict(
            response,
            preserving_proto_field_name=True
        )
    except RpcError as exc:
        handle_grpc_error(exc)


@app.get("/users/{user_id}")
def get_user(user_id: int):
    try:
        request = user_pb2.UserRequest(user_id=user_id)
        response = stub.GetUser(request, timeout=5)
        return MessageToDict(
            response,
            preserving_proto_field_name=True
        )
    except RpcError as exc:
        handle_grpc_error(exc)


@app.post("/users/", status_code=201)
def create_user(data: CreateUserRequest):
    try:
        request = user_pb2.CreateUserRequest(
            username=data.username,
            email=data.email,
            password=data.password
        )
        response = stub.CreateUser(request, timeout=5)
        return MessageToDict(
            response,
            preserving_proto_field_name=True
        )
    except RpcError as exc:
        handle_grpc_error(exc)


@app.patch("/users/{user_id}")
def update_user(user_id: int, data: UpdateUserRequest):
    try:
        request = user_pb2.UpdateUserRequest(
            user_id=user_id,
            username=data.username,
            email=data.email,
            password=data.password,
            role=data.role
        )
        response = stub.UpdateUser(request, timeout=5)
        return MessageToDict(
            response,
            preserving_proto_field_name=True
        )
    except RpcError as exc:
        handle_grpc_error(exc)


@app.post("/users/login")
def login(data: LoginRequest):
    try:
        request = user_pb2.LoginRequest(
            username=data.username,
            password=data.password
        )
        response = stub.Login(request, timeout=5)
        return MessageToDict(
            response,
            preserving_proto_field_name=True
        )
    except RpcError as exc:
        handle_grpc_error(exc)


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    try:
        request = user_pb2.UserRequest(user_id=user_id)
        response = stub.DeleteUser(request, timeout=5)
        return MessageToDict(
            response,
            preserving_proto_field_name=True
        )
    except RpcError as exc:
        handle_grpc_error(exc)
