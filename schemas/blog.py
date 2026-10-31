
from datetime import datetime

from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class TagResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class BlogBase(BaseModel):
    title: str
    slug: str
    seo_title: str | None = None
    description: str
    content: str | None = None


class BlogCreate(BlogBase):
    user_id: int
    file_id: int


class BlogUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    seo_title: str | None = None
    description: str | None = None
    content: str | None = None
    file_id: int | None = None


class BlogResponse(BlogBase):
    id: int
    view_num: int
    last_view_at: datetime | None
    user_id: int
    file_id: int
    path_photo: str | None = None
    created_at: datetime | None
    updated_at: datetime | None

    category: CategoryResponse | None = None
    tags: list[TagResponse] = []

    class Config:
        from_attributes = True


class BlogListResponse(BaseModel):
    page: int
    size: int
    total: int
    data: list[BlogResponse]
