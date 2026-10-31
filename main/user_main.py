
from fastapi import FastAPI

from scalar_fastapi import get_scalar_api_reference

from database import Base, engine

# Load all related models before creating tables
from tables.user import User
from tables.blog import Blog
from tables.category import Category
from tables.file import File
from tables.tag import Tag
from tables.blog_tag import BlogTag

from routes.user import router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="User Service API"
)


app.include_router(router)


@app.get(
    "/scalar",
    include_in_schema=False
)
def scalar():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main.user_main:app",
        host="127.0.0.1",
        port=7000,
        reload=True
    )
