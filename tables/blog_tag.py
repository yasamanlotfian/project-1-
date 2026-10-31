
from sqlalchemy import Column, Integer, ForeignKey

from database import Base


class BlogTag(Base):
    __tablename__ = "blog_tag"

    blog_id = Column(
        Integer,
        ForeignKey("blogs.id"),
        primary_key=True,
    )

    tag_id = Column(
        Integer,
        ForeignKey("Tags.id"),
        primary_key=True,
    )
