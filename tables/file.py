from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)

    original_file_url = Column(String(500), nullable=False)

    optimized_file_url = Column(String(500), nullable=True)

    crop_file_url = Column(String(500), nullable=True)

    original_file_size = Column(Integer, nullable=False)

    optimized_file_size = Column(Integer, nullable=True)

    crop_file_size = Column(Integer, nullable=True)


    mime_type = Column(String(50), nullable=False)


    file_type = Column(String(20), nullable=False)
    
    path_photo = Column(String(500), nullable=True)


    galleries = relationship(
        "Gallery",
        back_populates="file",
    )


    blogs = relationship(
        "Blog",
        back_populates="file",
    )