
import sys
from pathlib import Path

import grpc

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

FILE_GRPC_DIR = Path(__file__).resolve().parent
if str(FILE_GRPC_DIR) not in sys.path:
    sys.path.insert(0, str(FILE_GRPC_DIR))

import file_pb2
import file_pb2_grpc


class FileServiceClient:

    def __init__(self, address="localhost:5055"):
        self.channel = grpc.insecure_channel(address)
        self.stub = file_pb2_grpc.FileServiceStub(self.channel)

    def get_files(self):
        return self.stub.GetFiles(file_pb2.Empty())

    def get_file(self, file_id):
        return self.stub.GetFile(
            file_pb2.FileRequest(file_id=file_id)
        )

    def upload_file(self, file_path, file_type="file"):
        path = Path(file_path)

        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")

        content = path.read_bytes()

        import mimetypes
        mime_type = (
            mimetypes.guess_type(path.name)[0]
            or "application/octet-stream"
        )

        request = file_pb2.UploadFileRequest(
            filename=path.name,
            content=content,
            mime_type=mime_type,
            file_type=file_type,
        )

        return self.stub.UploadFile(request)

    def update_file(
        self,
        file_id,
        filename="",
        mime_type="",
        file_type="",
    ):
        request = file_pb2.UpdateFileRequest(
            file_id=file_id,
            filename=filename,
            mime_type=mime_type,
            file_type=file_type,
        )

        return self.stub.UpdateFile(request)

    def delete_file(self, file_id):
        return self.stub.DeleteFile(
            file_pb2.FileRequest(file_id=file_id)
        )

    def close(self):
        self.channel.close()


if __name__ == "__main__":
    client = FileServiceClient()

    try:
        result = client.get_files()

        for item in result.files:
            print(
                f"ID: {item.id} | "
                f"Filename: {item.filename} | "
                f"URL: {item.url}"
            )

    except grpc.RpcError as exc:
        print(f"gRPC error: {exc.code()} - {exc.details()}")

    finally:
        client.close()
