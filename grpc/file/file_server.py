
import sys
import uuid
import mimetypes
from pathlib import Path
from concurrent import futures
from io import BytesIO

import grpc
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy.orm import configure_mappers

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

FILE_GRPC_DIR = Path(__file__).resolve().parent

if str(FILE_GRPC_DIR) not in sys.path:
    sys.path.insert(0, str(FILE_GRPC_DIR))

import file_pb2
import file_pb2_grpc

from database import SessionLocal

from tables.user import User
from tables.blog import Blog
from tables.category import Category
from tables.file import File
from tables.tag import Tag
from tables.blog_tag import BlogTag

# بررسی ارتباط مدل‌های SQLAlchemy در همین پردازش
configure_mappers()


GALLERY_UPLOAD_DIR = PROJECT_ROOT / "uploads" / "gallery"

ORIGINAL_DIR = GALLERY_UPLOAD_DIR / "original"
WEBP_DIR = GALLERY_UPLOAD_DIR / "webp"
CROP_DIR = GALLERY_UPLOAD_DIR / "crop"

for folder in (ORIGINAL_DIR, WEBP_DIR, CROP_DIR):
    folder.mkdir(parents=True, exist_ok=True)

GRPC_PORT = 5055


def get_value(obj, *names, default=""):
    for name in names:
        if hasattr(obj, name):
            value = getattr(obj, name)
            if value is not None:
                return value
    return default


def make_file_response(file_obj):
    original_url = get_value(
        file_obj, "original_file_url", "url", "file_url"
    )
    optimized_url = get_value(
        file_obj, "optimized_file_url", default=""
    )
    crop_url = get_value(
        file_obj, "crop_file_url", default=""
    )

    return file_pb2.FileResponse(
        id=int(get_value(file_obj, "id", default=0)),
        filename=str(get_value(
            file_obj, "original_filename", "filename", "name",
            default=Path(str(original_url)).name
        )),
        url=str(original_url or ""),
        mime_type=str(get_value(file_obj, "mime_type")),
        file_type=str(get_value(file_obj, "file_type")),
        size=int(get_value(
            file_obj, "original_file_size", "size",
            "file_size", default=0
        )),
        created_at=str(get_value(file_obj, "created_at")),
        updated_at=str(get_value(file_obj, "updated_at")),
        original_file_url=str(original_url or ""),
        optimized_file_url=str(optimized_url or ""),
        crop_file_url=str(crop_url or ""),
    )


def find_file_path(file_obj):
    url = str(get_value(file_obj, "original_file_url"))
    if not url:
        return None

    stored_name = Path(url.replace("\\", "/")).name
    if not stored_name:
        return None

    for folder in (ORIGINAL_DIR, GALLERY_UPLOAD_DIR):
        candidate = (folder / stored_name).resolve()
        if candidate.parent == folder.resolve() and candidate.is_file():
            return candidate

    return ORIGINAL_DIR / stored_name


def safe_image_path(url, folder):
    if not url:
        return None

    stored_name = Path(str(url).replace("\\", "/")).name
    if not stored_name:
        return None

    candidate = (folder / stored_name).resolve()

    if candidate.parent != folder.resolve():
        return None

    return candidate


class FileService(file_pb2_grpc.FileServiceServicer):

    def GetFiles(self, request, context):
        db = SessionLocal()
        try:
            files = db.query(File).all()
            return file_pb2.FileList(
                files=[make_file_response(item) for item in files]
            )
        except Exception as exc:
            context.abort(
                grpc.StatusCode.INTERNAL,
                f"Could not get files: {exc}"
            )
        finally:
            db.close()

    def GetFile(self, request, context):
        db = SessionLocal()

        try:
            file_obj = db.query(File).filter(
                File.id == request.file_id
            ).first()

            if file_obj is not None:
                response = make_file_response(file_obj)
            else:
                response = None

        except Exception as exc:
            context.abort(
                grpc.StatusCode.INTERNAL,
                f"Could not get file: {str(exc)}"
            )

        finally:
            db.close()

        if response is None:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"File with ID {request.file_id} not found"
            )

        return response

    def UploadFile(self, request, context):
        if not request.filename:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Filename is required"
            )

        if not request.content:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "File content is empty"
            )

        db = SessionLocal()
        saved_paths = []

        try:
            original_name = Path(request.filename).name
            extension = Path(original_name).suffix.lower()
            stored_name = f"{uuid.uuid4().hex}{extension}"

            saved_path = ORIGINAL_DIR / stored_name
            saved_paths.append(saved_path)

            mime_type = (
                request.mime_type
                or mimetypes.guess_type(original_name)[0]
                or "application/octet-stream"
            )

            saved_path.write_bytes(request.content)

            optimized_url = None
            crop_url = None
            optimized_size = None
            crop_size = None

            if mime_type.startswith("image/"):
                try:
                    with Image.open(BytesIO(request.content)) as image:
                        image = ImageOps.exif_transpose(image)
                        image.load()

                        if image.mode not in ("RGB", "RGBA"):
                            image = image.convert("RGB")

                        webp_name = f"{uuid.uuid4().hex}.webp"
                        webp_path = WEBP_DIR / webp_name
                        saved_paths.append(webp_path)

                        webp_buffer = BytesIO()
                        image.save(
                            webp_buffer,
                            format="WEBP",
                            quality=85,
                            method=6
                        )

                        webp_content = webp_buffer.getvalue()
                        webp_path.write_bytes(webp_content)

                        optimized_url = (
                            f"/uploads/gallery/webp/{webp_name}"
                        )
                        optimized_size = len(webp_content)

                        crop_image = ImageOps.fit(
                            image,
                            (800, 800),
                            method=Image.Resampling.LANCZOS,
                            centering=(0.5, 0.5)
                        )

                        crop_name = f"{uuid.uuid4().hex}.webp"
                        crop_path = CROP_DIR / crop_name
                        saved_paths.append(crop_path)

                        crop_buffer = BytesIO()
                        crop_image.save(
                            crop_buffer,
                            format="WEBP",
                            quality=85,
                            method=6
                        )

                        crop_content = crop_buffer.getvalue()
                        crop_path.write_bytes(crop_content)

                        crop_url = (
                            f"/uploads/gallery/crop/{crop_name}"
                        )
                        crop_size = len(crop_content)

                except (
                    UnidentifiedImageError,
                    OSError,
                    ValueError
                ):
                    context.abort(
                        grpc.StatusCode.INVALID_ARGUMENT,
                        "Uploaded image is invalid or unsupported"
                    )

            file_obj = File(
                original_file_url=(
                    f"/uploads/gallery/original/{stored_name}"
                ),
                optimized_file_url=optimized_url,
                crop_file_url=crop_url,
                original_file_size=len(request.content),
                optimized_file_size=optimized_size,
                crop_file_size=crop_size,
                mime_type=mime_type,
                file_type=request.file_type or "image",
            )

            db.add(file_obj)
            db.commit()
            db.refresh(file_obj)

            return make_file_response(file_obj)

        except grpc.RpcError:
            db.rollback()
            for path in saved_paths:
                path.unlink(missing_ok=True)
            raise

        except Exception as exc:
            db.rollback()
            for path in saved_paths:
                path.unlink(missing_ok=True)

            context.abort(
                grpc.StatusCode.INTERNAL,
                f"File upload failed: {exc}"
            )

        finally:
            db.close()

    def UpdateFile(self, request, context):
        db = SessionLocal()
        try:
            file_obj = db.query(File).filter(
                File.id == request.file_id
            ).first()

            if file_obj is None:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "File not found"
                )

            if request.mime_type:
                file_obj.mime_type = request.mime_type

            if request.file_type:
                file_obj.file_type = request.file_type

            db.commit()
            db.refresh(file_obj)

            return make_file_response(file_obj)

        except grpc.RpcError:
            raise
        except Exception as exc:
            db.rollback()
            context.abort(
                grpc.StatusCode.INTERNAL,
                f"File update failed: {exc}"
            )
        finally:
            db.close()

    def DeleteFile(self, request, context):
        db = SessionLocal()
        try:
            file_obj = db.query(File).filter(
                File.id == request.file_id
            ).first()

            if file_obj is None:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "File not found"
                )

            file_paths = [
                find_file_path(file_obj),
                safe_image_path(
                    get_value(
                        file_obj,
                        "optimized_file_url",
                        default=""
                    ),
                    WEBP_DIR
                ),
                safe_image_path(
                    get_value(
                        file_obj,
                        "crop_file_url",
                        default=""
                    ),
                    CROP_DIR
                ),
            ]

            db.delete(file_obj)
            db.commit()

            for path in file_paths:
                if path and path.is_file():
                    path.unlink()

            return file_pb2.DeleteResponse(
                success=True,
                message="File deleted successfully"
            )

        except grpc.RpcError:
            raise
        except Exception as exc:
            db.rollback()
            context.abort(
                grpc.StatusCode.INTERNAL,
                f"File deletion failed: {exc}"
            )
        finally:
            db.close()


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    file_pb2_grpc.add_FileServiceServicer_to_server(
        FileService(), server
    )

    port = server.add_insecure_port(f"[::]:{GRPC_PORT}")
    if port == 0:
        raise RuntimeError(
            f"Could not bind gRPC server to port {GRPC_PORT}"
        )

    server.start()
    print(f"File gRPC Server running on port {GRPC_PORT}")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(grace=2)


if __name__ == "__main__":
    serve()
