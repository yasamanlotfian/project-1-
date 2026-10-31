
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from tables.comment import Comment
from tables.blog import Blog
from schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
)


router = APIRouter(
    prefix="/comments",
    tags=["Comment"]
)


@router.post(
    "/",
    response_model=CommentResponse,
    status_code=201,
)
def create_comment(
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
):
    blog = db.query(Blog).filter(
        Blog.id == comment_data.blog_id
    ).first()

    if blog is None:
        raise HTTPException(
            status_code=404,
            detail="Blog not found",
        )

    comment = Comment(
        name=comment_data.name,
        blog_id=comment_data.blog_id,
        content=comment_data.content,
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


@router.get(
    "/",
    response_model=list[CommentResponse],
)
def get_comments(
    db: Session = Depends(get_db),
):
    return (
        db.query(Comment)
        .order_by(Comment.created_at.desc())
        .all()
    )


@router.get(
    "/{comment_id}",
    response_model=CommentResponse,
    
)

def get_comment(
    comment_id: int,
    db: Session = Depends(get_db),
):
    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if comment is None:
        raise HTTPException(
            status_code=404,
            detail="Comment not found",
        )

    return comment


@router.patch(
    "/{comment_id}",
    response_model=CommentResponse
)
def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db),
):
    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if comment is None:
        raise HTTPException(
            status_code=404,
            detail="Comment not found",
        )

    update_data = comment_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(comment, field, value)

    db.commit()
    db.refresh(comment)

    return comment


@router.delete(
    "/{comment_id}",
)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
):
    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if comment is None:
        raise HTTPException(
            status_code=404,
            detail="Comment not found",
        )

    db.delete(comment)
    db.commit()

    return {
        "message": "Comment deleted successfully"
    }
