
import sys
from pathlib import Path

import grpc


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GALLERY_GRPC_DIR = PROJECT_ROOT / "grpc" / "gallery"

if str(GALLERY_GRPC_DIR) not in sys.path:
    sys.path.insert(0, str(GALLERY_GRPC_DIR))

import gallery_pb2
import gallery_pb2_grpc


class GalleryServiceClient:

    def __init__(self, address="localhost:5052"):
        self.channel = grpc.insecure_channel(address)
        self.stub = gallery_pb2_grpc.GalleryServiceStub(
            self.channel
        )

    def get_galleries(self, metadata=None):
        return self.stub.GetGalleries(
            gallery_pb2.Empty(),
            metadata=metadata,
            timeout=10,
        )

    def get_gallery(self, gallery_id: int, metadata=None):
        request = gallery_pb2.GalleryRequest(
            gallery_id=gallery_id
        )

        return self.stub.GetGallery(
            request,
            metadata=metadata,
            timeout=10,
        )

    def create_gallery(
        self,
        title: str,
        file_id: int,
        metadata=None,
    ):
        request = gallery_pb2.CreateGalleryRequest(
            title=title,
            file_id=file_id,
        )

        return self.stub.CreateGallery(
            request,
            metadata=metadata,
            timeout=10,
        )

    def update_gallery(
        self,
        gallery_id: int,
        title: str,
        file_id: int,
        metadata=None,
    ):
        request = gallery_pb2.UpdateGalleryRequest(
            gallery_id=gallery_id,
            title=title,
            file_id=file_id,
        )

        return self.stub.UpdateGallery(
            request,
            metadata=metadata,
            timeout=10,
        )

    def delete_gallery(self, gallery_id: int, metadata=None):
        request = gallery_pb2.DeleteGalleryRequest(
            gallery_id=gallery_id
        )

        return self.stub.DeleteGallery(
            request,
            metadata=metadata,
            timeout=10,
        )

    def get_gallery_by_file_id(
        self,
        file_id: int,
        metadata=None,
    ):
        request = gallery_pb2.FileRequest(
            file_id=file_id
        )

        return self.stub.GetGalleryByFileId(
            request,
            metadata=metadata,
            timeout=10,
        )

    def close(self):
        self.channel.close()
