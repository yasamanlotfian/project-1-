
from pathlib import Path
import sys

import grpc

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FILE_GRPC_DIR = PROJECT_ROOT / "grpc" / "file"

if str(FILE_GRPC_DIR) not in sys.path:
    sys.path.insert(0, str(FILE_GRPC_DIR))

import file_pb2
import file_pb2_grpc


class FileServiceClient:

    def __init__(self, address="localhost:5055"):
        self.channel = grpc.insecure_channel(address)
        self.stub = file_pb2_grpc.FileServiceStub(self.channel)

    def get_files(self):
        return self.stub.GetFiles(
            file_pb2.Empty(),
            timeout=10
        )

    def get_file(self, file_id: int):
        return self.stub.GetFile(
            file_pb2.FileRequest(file_id=file_id),
            timeout=10
        )

    def upload_file(
        self,
        filename: str,
        content: bytes,
        mime_type: str,
        file_type: str
    ):
        request = file_pb2.UploadFileRequest(
            filename=filename,
            content=content,
            mime_type=mime_type,
            file_type=file_type
        )

        return self.stub.UploadFile(request, timeout=30)

    def update_file(
        self,
        file_id: int,
        filename: str,
        mime_type: str,
        file_type: str
    ):
        request = file_pb2.UpdateFileRequest(
            file_id=file_id,
            filename=filename,
            mime_type=mime_type,
            file_type=file_type
        )

        return self.stub.UpdateFile(request, timeout=10)

    def delete_file(self, file_id: int):
        return self.stub.DeleteFile(
            file_pb2.FileRequest(file_id=file_id),
            timeout=10
        )

    def close(self):
        self.channel.close()
