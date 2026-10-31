
import sys
from pathlib import Path

import grpc

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GALLERY_GRPC_DIR = PROJECT_ROOT / "grpc" / "gallery"

if str(GALLERY_GRPC_DIR) not in sys.path:
    sys.path.insert(0, str(GALLERY_GRPC_DIR))

import gallery_pb2
import gallery_pb2_grpc


def run():
    channel = grpc.insecure_channel("localhost:5052")
    stub = gallery_pb2_grpc.GalleryServiceStub(channel)

    try:
        print("\nALL GALLERIES")

        response = stub.GetGalleries(
            gallery_pb2.Empty(), timeout=10
        )

        for gallery in response.galleries:
            print("ID:", gallery.id)
            print("Title:", gallery.title)
            print("File ID:", gallery.file_id)

        print("\nGET GALLERY")

        response = stub.GetGallery(
            gallery_pb2.GalleryRequest(gallery_id=1),
            timeout=10
        )

        print("ID:", response.id)
        print("Title:", response.title)
        print("File ID:", response.file_id)

        print("\nCREATE GALLERY")

        response = stub.CreateGallery(
            gallery_pb2.CreateGalleryRequest(
                title="Hair Salon",
                file_id=1
            ),
            timeout=10
        )

        print("Created ID:", response.id)
        print("Title:", response.title)
        print("File ID:", response.file_id)

        created_gallery_id = response.id

        print("\nUPDATE GALLERY")

        response = stub.UpdateGallery(
            gallery_pb2.UpdateGalleryRequest(
                gallery_id=created_gallery_id,
                title="Updated Hair Salon",
                file_id=1
            ),
            timeout=10
        )

        print("Updated ID:", response.id)
        print("Title:", response.title)
        print("File ID:", response.file_id)

        print("\nDELETE GALLERY")

        response = stub.DeleteGallery(
            gallery_pb2.DeleteGalleryRequest(
                gallery_id=created_gallery_id
            ),
            timeout=10
        )

        print("Deleted successfully")

    except grpc.RpcError as exc:
        print("gRPC error:", exc.code(), exc.details())

    finally:
        channel.close()


if __name__ == "__main__":
    run()
