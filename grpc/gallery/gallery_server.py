
import sys
import traceback
from concurrent import futures

import grpc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import configure_mappers

sys.path.insert(0, r"C:\Users\lotus\project")
sys.path.insert(0, r"C:\Users\lotus\project\grpc\gallery")

from database import SessionLocal

import tables
configure_mappers()

from tables.gallery import Gallery
from service.file_service import FileServiceClient

import gallery_pb2
import gallery_pb2_grpc


class GalleryService(gallery_pb2_grpc.GalleryServiceServicer):


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

        file_info = self.get_file_info(gallery.file_id, context)

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

    def validate_title(self, title, context):

        if not title or not title.strip():
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Title cannot be empty",
            )

 

    def GetGalleries(self, request, context):

        print("GetGalleries request received")

        db = SessionLocal()

        try:
            galleries = db.query(Gallery).all()
            print("Galleries count:", len(galleries))

        except Exception as exc:
            print("GetGalleries database error:", repr(exc))
            traceback.print_exc()

            context.abort(
                grpc.StatusCode.INTERNAL,
                f"GetGalleries database error: {str(exc)}",
            )

        finally:
            db.close()

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

            response.galleries.add().CopyFrom(gallery_response)

        print("GetGalleries completed successfully")

        return response



    def GetGallery(self, request, context):

        print("GetGallery request received")
        print("Gallery ID:", request.gallery_id)

        db = SessionLocal()
        gallery = None

        try:
            gallery = db.query(Gallery).filter(
                Gallery.id == request.gallery_id
            ).first()

        except Exception as exc:
            print("GetGallery database error:", repr(exc))
            traceback.print_exc()

            context.abort(
                grpc.StatusCode.INTERNAL,
                f"GetGallery database error: {str(exc)}",
            )

        finally:
            db.close()

        if gallery is None:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                "Gallery not found",
            )

        return self.make_gallery_response(gallery, context)


    def CreateGallery(self, request, context):

        print("CreateGallery request received")

        self.validate_title(request.title, context)
        self.validate_file(request.file_id, context)

        db = SessionLocal()
        gallery = None

        try:
            gallery = Gallery(
                title=request.title.strip(),
                file_id=request.file_id,
            )

            db.add(gallery)
            db.commit()
            db.refresh(gallery)

            print("Gallery created:", gallery.id)

        except IntegrityError as exc:
            db.rollback()

            print("CreateGallery IntegrityError:", repr(exc))

            context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                "Gallery could not be created because of a database constraint",
            )

        except Exception as exc:
            db.rollback()

            print("CreateGallery error:", repr(exc))
            traceback.print_exc()

            context.abort(
                grpc.StatusCode.INTERNAL,
                f"CreateGallery failed: {str(exc)}",
            )

        finally:
            db.close()

        return self.make_gallery_response(gallery, context)

 

    def UpdateGallery(self, request, context):

        print("UpdateGallery request received")
        print("Gallery ID:", request.gallery_id)

        db = SessionLocal()
        gallery = None

        try:
            gallery = db.query(Gallery).filter(
                Gallery.id == request.gallery_id
            ).first()

        except Exception as exc:
            print("UpdateGallery query error:", repr(exc))
            traceback.print_exc()

            context.abort(
                grpc.StatusCode.INTERNAL,
                f"UpdateGallery query failed: {str(exc)}",
            )

        if gallery is None:
            db.close()

            context.abort(
                grpc.StatusCode.NOT_FOUND,
                "Gallery not found",
            )

        try:
            self.validate_title(request.title, context)
            self.validate_file(request.file_id, context)

            gallery.title = request.title.strip()
            gallery.file_id = request.file_id

            db.commit()
            db.refresh(gallery)

            print("Gallery updated:", request.gallery_id)

        except IntegrityError as exc:
            db.rollback()

            print("UpdateGallery IntegrityError:", repr(exc))

            context.abort(
                grpc.StatusCode.FAILED_PRECONDITION,
                "Gallery update conflicts with a database constraint",
            )

        except Exception as exc:
            db.rollback()

            print("UpdateGallery error:", repr(exc))
            traceback.print_exc()

            context.abort(
                grpc.StatusCode.INTERNAL,
                f"UpdateGallery failed: {str(exc)}",
            )

        finally:
            db.close()

        return self.make_gallery_response(gallery, context)


    def DeleteGallery(self, request, context):

        print("DeleteGallery request received")
        print("Gallery ID:", request.gallery_id)

        db = SessionLocal()
        response = None

        try:
            gallery = db.query(Gallery).filter(
                Gallery.id == request.gallery_id
            ).first()

            if gallery is not None:

                response = gallery_pb2.GalleryResponse(
                    id=gallery.id,
                    title=gallery.title,
                    file_id=gallery.file_id,
                )

                db.delete(gallery)
                db.commit()

                print("Gallery deleted:", request.gallery_id)

        except IntegrityError as exc:
            db.rollback()

            print("DeleteGallery IntegrityError:", repr(exc))
            traceback.print_exc()

            context.abort(
                grpc.StatusCode.FAILED_PRECONDITION,
                "Cannot delete gallery because related records exist",
            )

        except Exception as exc:
            db.rollback()

            print("DeleteGallery error:", repr(exc))
            traceback.print_exc()

            context.abort(
                grpc.StatusCode.INTERNAL,
                f"DeleteGallery failed: {str(exc)}",
            )

        finally:
            db.close()

        if response is None:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                "Gallery not found",
            )

        return response


    def GetGalleryByFileId(self, request, context):

        print("GetGalleryByFileId request received")

        db = SessionLocal()
        gallery = None

        try:
            gallery = db.query(Gallery).filter(
                Gallery.file_id == request.file_id
            ).first()

        except Exception as exc:
            print("GetGalleryByFileId database error:", repr(exc))
            traceback.print_exc()

            context.abort(
                grpc.StatusCode.INTERNAL,
                f"GetGalleryByFileId failed: {str(exc)}",
            )

        finally:
            db.close()

        if gallery is None:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                "Gallery not found for this file",
            )

        return self.make_gallery_response(gallery, context)


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
