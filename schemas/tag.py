
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TagCreate(BaseModel):
    name: str


class TagUpdate(BaseModel):
    name: str | None = None


class TagResponse(BaseModel):
    id: int

    name: str

    created_at: datetime | None = None

    updated_at: datetime | None = None
    

    model_config = ConfigDict(from_attributes=True)
