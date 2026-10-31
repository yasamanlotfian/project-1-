
from sqlalchemy import (
    Column, Integer, String, Text,
    DateTime, ForeignKey
)
from sqlalchemy.sql import func

from database import Base


class Comment(Base):

    __tablename__ = "comments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(255),
        nullable=False
    )

    blog_id = Column(
        Integer,
        ForeignKey("blogs.id"),
        nullable=False,
        index=True
    )

    content = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
