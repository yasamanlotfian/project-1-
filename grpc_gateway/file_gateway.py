
import sys
from pathlib import Path

import grpc
from fastapi import FastAPI, HTTPException, UploadFile, File
from google.protobuf.json_format import MessageToDict
from scalar_fastapi import get_scalar_api_reference

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FILE_GRPC_DIR = PROJECT_ROOT / "grpc" / "file"

if str(FILE_GRPC_DIR) not in sys.path:
    sys.path.insert(0, str(FILE_GRPC_DIR))

import file_pb2
import file_pb2_grpc


app = FastAPI(
    title="File Service API",
    description="File management API using gRPC",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
)


def get_stub():
    channel = grpc.insecure_channel("127.0.0.1:5055")
    stub = file_pb2_grpc.FileServiceStub(channel)
    return channel, stub


def to_dict(message):
    return MessageToDict(
        message,
        preserving_proto_field_name=True,
    )


def grpc_error(exc):
    raise HTTPException(
        status_code=(
            503
            if exc.code() == grpc.StatusCode.UNAVAILABLE
            else 500
        ),
        detail=exc.details() or "gRPC request failed",
    )


@app.post("/upload")
async def upload_file(upload: UploadFile = File(...)):
    content = await upload.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty",
        )

    channel, stub = get_stub()

    try:
        request = file_pb2.UploadFileRequest(
            filename=upload.filename or "upload.bin",
            content=content,
        )

        result = stub.UploadFile(request, timeout=30)
        return to_dict(result)

    except grpc.RpcError as exc:
        grpc_error(exc)

    finally:
        channel.close()


@app.get("/scalar", include_in_schema=False)
async def scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )
