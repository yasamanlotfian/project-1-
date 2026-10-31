
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from database import get_db
from tables.blog import Blog
from schemas.blog import (
    BlogCreate,
    BlogUpdate,
    BlogResponse,
    BlogListResponse
)


router = APIRouter(
    prefix="/blogs",
    tags=["Blog"]
)


def validate_pagination(
    page: int,
    size: int
):
    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="Page must be greater than 0"
        )

    if size < 1:
        raise HTTPException(
            status_code=400,
            detail="Size must be greater than 0"
        )

    if size > 10:
        raise HTTPException(
            status_code=400,
            detail="Size cannot be greater than 10"
        )


def get_sort_column(
    sort_by: str
):
    sort_by = sort_by.strip().lower()

    allowed_sort_fields = {
        "id": Blog.id,
        "title": Blog.title,
        "seo_title": Blog.seo_title,
        "slug": Blog.slug,
        "view_num": Blog.view_num,
        "created_at": Blog.created_at,
        "updated_at": Blog.updated_at
    }

    column = allowed_sort_fields.get(sort_by)

    if column is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid sort_by. "
                "Allowed values: "
                "id, title, seo_title, slug, "
                "view_num, created_at, updated_at"
            )
        )

    return column


def get_order_column(
    column,
    sort_order: str
):
    sort_order = sort_order.strip().lower()

    if sort_order == "asc":
        return column.asc()

    if sort_order == "desc":
        return column.desc()

    raise HTTPException(
        status_code=400,
        detail="sort_order must be 'asc' or 'desc'"
    )


@router.get(
    "/",
    response_model=BlogListResponse
)
def get_blogs(
    page: int = 1,
    size: int = 5,
    search: str | None = None,
    sort_by: str = "id",
    sort_order: str = "desc",
    db: Session = Depends(get_db)
):
    validate_pagination(
        page,
        size
    )

    column = get_sort_column(
        sort_by
    )

    order_column = get_order_column(
        column,
        sort_order
    )

    query = (
        db.query(Blog)
        .options(
            selectinload(Blog.category),
            selectinload(Blog.tags)
        )
    )

    if search:
        search_text = f"%{search.strip()}%"

        query = query.filter(
            Blog.title.ilike(search_text)
            | Blog.description.ilike(search_text)
            | Blog.content.ilike(search_text)
        )

    total = query.count()

    blogs = (
        query
        .order_by(order_column)
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return {
        "page": page,
        "size": size,
        "total": total,
        "data": blogs
    }


@router.get(
    "/{slug}",
    response_model=BlogResponse
)
def get_blog(
    slug: str,
    db: Session = Depends(get_db)
):
    blog = (
        db.query(Blog)
        .options(
            selectinload(Blog.category),
            selectinload(Blog.tags)
        )
        .filter(Blog.slug == slug)
        .first()
    )

    if not blog:
        raise HTTPException(
            status_code=404,
            detail="Blog not found"
        )

    now = datetime.now(timezone.utc)

    if (
        blog.last_view_at is None
        or now - blog.last_view_at
        >= timedelta(minutes=1)
    ):
        blog.view_num += 1
        blog.last_view_at = now

        db.commit()
        db.refresh(blog)

    return blog


@router.post(
    "/",
    response_model=BlogResponse
)
def create_blog(
    blog_data: BlogCreate,
    db: Session = Depends(get_db)
):
    existing_blog = (
        db.query(Blog)
        .filter(Blog.slug == blog_data.slug)
        .first()
    )

    if existing_blog:
        raise HTTPException(
            status_code=400,
            detail="Slug already exists"
        )

    blog = Blog(
        title=blog_data.title,
        slug=blog_data.slug,
        seo_title=blog_data.seo_title,
        description=blog_data.description,
        content=blog_data.content,
        user_id=blog_data.user_id,
        file_id=blog_data.file_id,
        view_num=0,
        last_view_at=None
    )

    db.add(blog)
    db.commit()
    db.refresh(blog)

    return blog


@router.patch(
    "/{blog_id}",
    response_model=BlogResponse
)
def update_blog(
    blog_id: int,
    blog_data: BlogUpdate,
    db: Session = Depends(get_db)
):
    blog = (
        db.query(Blog)
        .filter(Blog.id == blog_id)
        .first()
    )

    if not blog:
        raise HTTPException(
            status_code=404,
            detail="Blog not found"
        )

    update_data = blog_data.model_dump(
        exclude_unset=True
    )

    if "slug" in update_data:
        existing_blog = (
            db.query(Blog)
            .filter(
                Blog.slug == update_data["slug"],
                Blog.id != blog.id
            )
            .first()
        )

        if existing_blog:
            raise HTTPException(
                status_code=400,
                detail="Slug already exists"
            )

    for field, value in update_data.items():
        setattr(
            blog,
            field,
            value
        )

    db.commit()
    db.refresh(blog)

    return blog


@router.delete(
    "/{blog_id}"
)
def delete_blog(
    blog_id: int,
    db: Session = Depends(get_db)
):
    blog = (
        db.query(Blog)
        .filter(Blog.id == blog_id)
        .first()
    )

    if not blog:
        raise HTTPException(
            status_code=404,
            detail="Blog not found"
        )

    db.delete(blog)
    db.commit()

    return {
        "message": "Blog deleted successfully"
    }
