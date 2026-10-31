

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    name: str


class CategoryUpdate(BaseModel):
    name: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int

    name: str

    created_at: Optional[datetime] = None
    
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
