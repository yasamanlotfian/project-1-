
from fastapi import FastAPI

from scalar_fastapi import get_scalar_api_reference

from database import Base, engine

from tables.gallery import Gallery


from routes.gallery import router

Base.metadata.create_all(
    bind=engine
)
 
app = FastAPI(
    title="Gallery Service API"
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
        "main.gallery_main:app",
        host="127.0.0.1",
        port=7001,
        reload=True
    )