
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True)

    title = Column(String(255), nullable=False)

    slug = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    seo_title = Column(String(255), nullable=True)

    description = Column(Text, nullable=False)

    content = Column(Text, nullable=True)

    file_id = Column(
        Integer,
        ForeignKey("files.id"),
        nullable=True,
        index=True,
    )

    file = relationship(
        "File",
        back_populates="blogs",
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=True,
        index=True,
    )

    category = relationship(
        "Category",
        back_populates="blogs",
    )

    view_num = Column(
        Integer,
        default=0,
        nullable=False,
        index=True,
    )

    last_view_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    user_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    tags = relationship(
        "Tag",
        secondary="blog_tag",
        back_populates="blogs",
    )
