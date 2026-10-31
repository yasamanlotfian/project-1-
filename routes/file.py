
import grpc

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
)

from service.file_service import FileServiceClient


router = APIRouter(
    prefix="/file",
    tags=["File"],
)


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
):
    client = FileServiceClient()

    try:
        if not file.content_type:
            raise HTTPException(
                status_code=400,
                detail="File content type is missing",
            )

        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="Only image files are allowed",
            )

        content = await file.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty",
            )

        result = client.upload_file(
            filename=file.filename or "image",
            content=content,
            mime_type=file.content_type,
            file_type="image",
        )

        return {
            "message": "File uploaded successfully",
            "file_id": result.id,
            "file_type": result.file_type,
            "mime_type": result.mime_type,
            "original_file_url": result.url,
            "optimized_file_url": None,
            "crop_file_url": None,
            "original_file_size": result.size,
            "optimized_file_size": None,
            "crop_file_size": None,
        }

    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
            status_code = 400
        elif e.code() == grpc.StatusCode.UNAVAILABLE:
            status_code = 503
        else:
            status_code = 500

        raise HTTPException(
            status_code=status_code,
            detail=e.details() or "File upload failed",
        )

    finally:
        client.close()
        await file.close()
