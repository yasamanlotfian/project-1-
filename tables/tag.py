
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Tag(Base):
    __tablename__ = "Tags"

    id = Column(
        Integer,
        primary_key=True
    )

    name = Column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    blogs = relationship(
        "Blog",
        secondary="blog_tag",
        back_populates="tags"
    )
