from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GalleryBase(BaseModel):
    title:str
    file_id: int


class GalleryCreate(GalleryBase):
    file_id: int


class GalleryUpdate(BaseModel):
    file_id: int | None = None


class GalleryResponse(GalleryBase):
    id: int

    file_id :int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    original_file_url: str
    optimized_file_url: str | None = None
    crop_file_url: str | None = None

    original_file_size: int
    optimized_file_size: int | None = None
    crop_file_size: int | None = None

    mime_type: str
    file_type: str

    model_config = ConfigDict(from_attributes=True)