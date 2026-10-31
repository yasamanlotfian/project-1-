from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from tables.tag import Tag

from schemas.tag import (
    TagCreate,
    TagUpdate,
    TagResponse
)

router = APIRouter(
    prefix="/tag",
    tags=["Tag"]
)



@router.post(
    "/",
    response_model=TagResponse,
)

def create_tag(
    tag_data: TagCreate,
    db: Session = Depends(get_db)
):
    tag = Tag(
        name=tag_data.name
    )

    db.add(tag)
    db.commit()
    db.refresh(tag)

    return tag


@router.get(
       "/",
    response_model=list[TagResponse],
)

def get_tags(
    db: Session = Depends(get_db)
):
    return db.query(Tag).all()



@router.get(
    "/{tag_id}",
    response_model=TagResponse,
)

def get_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    tag = (
        db.query(Tag)
        .filter(Tag.id == tag_id)
        .first()
    )

    if not tag:
        raise HTTPException(
            status_code=404,
            detail="Tag not found"
        )

    return tag



@router.patch(
    "/{tag_id}",
    response_model=TagResponse
)
def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    db: Session = Depends(get_db)
):
    tag = (
        db.query(Tag)
        .filter(Tag.id == tag_id)
        .first()
    )

    if not tag:
        raise HTTPException(
            status_code=404,
            detail="Tag not found"
        )

    if tag_data.name is not None:
        tag.name = tag_data.name

    db.commit()
    db.refresh(tag)

    return tag


@router.delete(
    "/{tag_id}",
)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    tag = (
        db.query(Tag)
        .filter(Tag.id == tag_id)
        .first()
    )

    if not tag:
        raise HTTPException(
            status_code=404,
            detail="Tag not found"
        )

    db.delete(tag)
    db.commit()

    return {
        "message": "Tag deleted successfully"
    }
