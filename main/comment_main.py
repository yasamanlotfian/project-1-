
from fastapi import FastAPI

from scalar_fastapi import get_scalar_api_reference

from database import Base, engine

from tables.blog import Blog
from tables.comment import Comment

from routes.comment import router


Comment.__table__.create(
    bind=engine,
    checkfirst=True
)


app = FastAPI(
    title="Comment Service API",
    version="1.0.0"
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
        "main.comment_main:app",
        host="127.0.0.1",
        port=7005,
        reload=True
    )
