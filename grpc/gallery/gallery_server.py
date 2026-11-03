
import sys
import traceback
from concurrent import futures

import grpc

sys.path.insert(0, r"C:\Users\lotus\project")
sys.path.insert(0, r"C:\Users\lotus\project\grpc\gallery")

from database import SessionLocal

import tables
from sqlalchemy.orm import configure_mappers

configure_mappers()

from tables.gallery import Gallery
from service.file_service import FileServiceClient

import gallery_pb2
import gallery_pb2_grpc


class GalleryService(
    gallery_pb2_grpc.GalleryServiceServicer
):

    def get_file_info(self, file_id, context):
  

        if not file_id:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "file_id is required",
            )

        client = FileServiceClient("localhost:5055")

        try:
            return client.get_file(file_id)

        except grpc.RpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    f"File ID {file_id} not found in File Service",
                )

            context.abort(
                grpc.StatusCode.UNAVAILABLE,
                f"Could not access File Service: {exc.details()}",
            )

        finally:
            client.close()

    def make_gallery_response(self, gallery, context):
   

        file_info = self.get_file_info(
            gallery.file_id,
            context,
        )

        return gallery_pb2.GalleryResponse(
            id=gallery.id,
            title=gallery.title,
            file_id=gallery.file_id,

            filename=file_info.filename,
            original_file_url=file_info.original_file_url,
            optimized_file_url=file_info.optimized_file_url,
            crop_file_url=file_info.crop_file_url,
            mime_type=file_info.mime_type,
            file_type=file_info.file_type,
        )

    def validate_file(self, file_id, context):

        self.get_file_info(file_id, context)

    def GetGalleries(self, request, context):

        print("GetGalleries request received")

        db = SessionLocal()

        try:
            galleries = db.query(Gallery).all()

            print("Galleries count:", len(galleries))

            response = gallery_pb2.GalleryList()

            for gallery in galleries:

                print(
                    "Processing gallery:",
                    gallery.id,
                    gallery.title,
                    gallery.file_id,
                )

                gallery_response = self.make_gallery_response(
                    gallery,
                    context,
                )

                response.galleries.add().CopyFrom(
                    gallery_response
                )

            print("GetGalleries completed successfully")

            return response

        except grpc.RpcError:
            traceback.print_exc()
            raise

        except Exception as exc:

            db.rollback()

            print("ERROR TYPE:", type(exc).__name__)
            print("ERROR REPR:", repr(exc))
            traceback.print_exc()

            context.abort(
                grpc.StatusCode.INTERNAL,
                f"GetGalleries failed: {type(exc).__name__}: {repr(exc)}",
            )

        finally:
            db.close()

    def GetGallery(self, request, context):

        print("GetGallery request received")

        db = SessionLocal()

        try:
            gallery = db.query(Gallery).filter(
                Gallery.id == request.gallery_id
            ).first()

            if gallery is None:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Gallery not found",
                )

            return self.make_gallery_response(
                gallery,
                context,
            )

        except grpc.RpcError:
            raise

        except Exception as exc:

            print("GetGallery error:", repr(exc))
            traceback.print_exc()

            context.abort(
                grpc.StatusCode.INTERNAL,
                f"GetGallery failed: {type(exc).__name__}: {repr(exc)}",
            )

        finally:
            db.close()

    def CreateGallery(self, request, context):

        print("CreateGallery request received")

        self.validate_file(request.file_id, context)

        db = SessionLocal()

        try:
            gallery = Gallery(
                title=request.title,
                file_id=request.file_id,
            )

            db.add(gallery)
            db.commit()
            db.refresh(gallery)

            return self.make_gallery_response(
                gallery,
                context,
            )

        except grpc.RpcError:
            db.rollback()
            raise

        except Exception as exc:

            db.rollback()

            print("CreateGallery error:", repr(exc))
            traceback.print_exc()

            context.abort(
                grpc.StatusCode.INTERNAL,
                f"CreateGallery failed: {type(exc).__name__}: {repr(exc)}",
            )

        finally:
            db.close()

    def UpdateGallery(self, request, context):

        print("UpdateGallery request received")

        self.validate_file(request.file_id, context)

        db = SessionLocal()

        try:
            gallery = db.query(Gallery).filter(
                Gallery.id == request.gallery_id
            ).first()

            if gallery is None:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Gallery not found",
                )

            gallery.title = request.title
            gallery.file_id = request.file_id

            db.commit()
            db.refresh(gallery)

            return self.make_gallery_response(
                gallery,
                context,
            )

        except grpc.RpcError:
            db.rollback()
            raise

        except Exception as exc:

            db.rollback()

            print("UpdateGallery error:", repr(exc))
            traceback.print_exc()

            context.abort(
                grpc.StatusCode.INTERNAL,
                f"UpdateGallery failed: {type(exc).__name__}: {repr(exc)}",
            )

        finally:
            db.close()

    def DeleteGallery(self, request, context):

        print("DeleteGallery request received")

        db = SessionLocal()

        try:
            gallery = db.query(Gallery).filter(
                Gallery.id == request.gallery_id
            ).first()

            if gallery is None:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Gallery not found",
                )

            response = gallery_pb2.GalleryResponse(
                id=gallery.id,
                title=gallery.title,
                file_id=gallery.file_id,
            )

            db.delete(gallery)
            db.commit()

            print("Gallery deleted:", request.gallery_id)

            return response

        except grpc.RpcError:
            db.rollback()
            raise

        except Exception as exc:

            db.rollback()

            print("DeleteGallery error:", repr(exc))
            traceback.print_exc()

            context.abort(
                grpc.StatusCode.INTERNAL,
                f"DeleteGallery failed: {type(exc).__name__}: {repr(exc)}",
            )

        finally:
            db.close()

    def GetGalleryByFileId(self, request, context):

        print("GetGalleryByFileId request received")

        db = SessionLocal()

        try:
            gallery = db.query(Gallery).filter(
                Gallery.file_id == request.file_id
            ).first()

            if gallery is None:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Gallery not found for this file",
                )

            return self.make_gallery_response(
                gallery,
                context,
            )

        except grpc.RpcError:
            raise

        except Exception as exc:

            print("GetGalleryByFileId error:", repr(exc))
            traceback.print_exc()

            context.abort(
                grpc.StatusCode.INTERNAL,
                f"GetGalleryByFileId failed: {type(exc).__name__}: {repr(exc)}",
            )

        finally:
            db.close()


def serve():

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    gallery_pb2_grpc.add_GalleryServiceServicer_to_server(
        GalleryService(),
        server,
    )

    port = server.add_insecure_port("[::]:5052")

    if port == 0:
        raise RuntimeError(
            "Could not bind gRPC server to port 5052"
        )

    server.start()

    print("Gallery gRPC Server running on port 5052")

    try:
        server.wait_for_termination()

    except KeyboardInterrupt:
        server.stop(grace=2)


if __name__ == "__main__":
    serve()
