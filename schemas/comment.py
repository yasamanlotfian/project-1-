
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CommentCreate(BaseModel):
    name: str
    blog_id: int
    content: str


class CommentUpdate(BaseModel):
    name: str | None = None
    content: str | None = None


class CommentResponse(BaseModel):
    id: int
    name: str
    blog_id: int
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
