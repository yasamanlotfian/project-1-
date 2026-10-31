
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from tables.gallery import Gallery
from tables.file import File
from schemas.gallery import (
    GalleryCreate,
    GalleryUpdate,
    GalleryResponse,
)

router = APIRouter(
    prefix="/galleries",
    tags=["Gallery"],
)


@router.post("/")
def create_gallery(
    gallery_data: GalleryCreate,
    db: Session = Depends(get_db),
):
    file = (
        db.query(File)
        .filter(File.id == gallery_data.file_id)
        .first()
    )

    if file is None:
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    new_gallery = Gallery(
        title=gallery_data.title,
        file_id=gallery_data.file_id,
        alt_text=gallery_data.alt_text,
    )

    db.add(new_gallery)
    db.commit()
    db.refresh(new_gallery)

    return {
        "gallery_id": new_gallery.id,
        "file_id": file.id,
        "original_file_url": file.original_file_url,
        "optimized_file_url": file.optimized_file_url,
        "crop_file_url": file.crop_file_url,
        "alt_text": new_gallery.alt_text,
    }


@router.get("/")
def get_galleries(
    db: Session = Depends(get_db),
):
    galleries = (
        db.query(Gallery, File)
        .join(File, Gallery.file_id == File.id)
        .all()
    )

    return [
        {
            "gallery_id": gallery.id,
            "file_id": file.id,
            "original_file_url": file.original_file_url,
            "optimized_file_url": file.optimized_file_url,
            "crop_file_url": file.crop_file_url,
            "alt_text": gallery.alt_text,
        }
        for gallery, file in galleries
    ]


@router.get("/{gallery_id}")
def get_gallery(
    gallery_id: int,
    db: Session = Depends(get_db),
):
    result = (
        db.query(Gallery, File)
        .join(File, Gallery.file_id == File.id)
        .filter(Gallery.id == gallery_id)
        .first()
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Gallery not found",
        )

    gallery, file = result

    return {
        "gallery_id": gallery.id,
        "file_id": file.id,
        "original_file_url": file.original_file_url,
        "optimized_file_url": file.optimized_file_url,
        "crop_file_url": file.crop_file_url,
        "alt_text": gallery.alt_text,
    }


@router.patch("/{gallery_id}", response_model=GalleryResponse)
def update_gallery(
    gallery_id: int,
    gallery_data: GalleryUpdate,
    db: Session = Depends(get_db),
):
    gallery = (
        db.query(Gallery)
        .filter(Gallery.id == gallery_id)
        .first()
    )

    if gallery is None:
        raise HTTPException(
            status_code=404,
            detail="Gallery not found",
        )

    update_data = gallery_data.model_dump(exclude_unset=True)

    if "file_id" in update_data:
        file = (
            db.query(File)
            .filter(File.id == update_data["file_id"])
            .first()
        )

        if file is None:
            raise HTTPException(
                status_code=404,
                detail="File not found",
            )

    for field, value in update_data.items():
        setattr(gallery, field, value)

    db.commit()
    db.refresh(gallery)

    return gallery


@router.delete("/{gallery_id}")
def delete_gallery(
    gallery_id: int,
    db: Session = Depends(get_db),
):
    gallery = (
        db.query(Gallery)
        .filter(Gallery.id == gallery_id)
        .first()
    )

    if gallery is None:
        raise HTTPException(
            status_code=404,
            detail="Gallery not found",
        )

    db.delete(gallery)
    db.commit()

    return {
        "message": "Gallery deleted successfully"
    }
