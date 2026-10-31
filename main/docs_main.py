
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

import requests
import copy


app = FastAPI(
    title="Hair Salon Blog System API",
    version="1.0.0",
    openapi_url=None,
    docs_url=None,
    redoc_url=None
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SERVICES = {
    "user": "http://127.0.0.1:7000/openapi.json",
    "blog": "http://127.0.0.1:7002/openapi.json",
    "gallery": "http://127.0.0.1:7001/openapi.json",
    "file": "http://127.0.0.1:7006/openapi.json",
    "comment": "http://127.0.0.1:7005/openapi.json",
    "tag": "http://127.0.0.1:7007/openapi.json",
    "category": "http://127.0.0.1:7008/openapi.json",
    "aggregation": "http://127.0.0.1:7009/openapi.json"
}


def replace_refs(obj, schema_names):

    if isinstance(obj, dict):

        for key, value in obj.items():

            if key == "$ref" and isinstance(value, str):

                prefix = "#/components/schemas/"

                if value.startswith(prefix):

                    old_name = value[len(prefix):]

                    if old_name in schema_names:

                        obj[key] = (
                            prefix + schema_names[old_name]
                        )

            else:

                replace_refs(
                    value,
                    schema_names
                )

    elif isinstance(obj, list):

        for item in obj:

            replace_refs(
                item,
                schema_names
            )


@app.get(
    "/openapi.json",
    include_in_schema=False
)
def combined_openapi():

    combined_api = {

        "openapi": "3.1.0",

        "info": {
            "title": "Hair Salon Blog System API",
            "version": "1.0.0"
        },

        "paths": {},

        "components": {
            "schemas": {}
        }
    }

    for service_name, url in SERVICES.items():

        print(
            f"Loading {service_name}: {url}"
        )

        response = requests.get(
            url,
            timeout=20
        )

        response.raise_for_status()

        service_api = response.json()

        schemas = (
            service_api
            .get("components", {})
            .get("schemas", {})
        )

        schema_names = {

            old_name:
            f"{service_name}_{old_name}"

            for old_name in schemas
        }

        for old_name, schema in schemas.items():

            new_name = schema_names[
                old_name
            ]

            schema_copy = copy.deepcopy(
                schema
            )

            replace_refs(
                schema_copy,
                schema_names
            )

            combined_api[
                "components"
            ][
                "schemas"
            ][
                new_name
            ] = schema_copy

        for path, methods in (
            service_api
            .get("paths", {})
            .items()
        ):

            new_path = (
                f"/{service_name}{path}"
            )

            methods_copy = copy.deepcopy(
                methods
            )

            replace_refs(
                methods_copy,
                schema_names
            )

            combined_api[
                "paths"
            ][
                new_path
            ] = methods_copy

    print(
        "Combined paths:",
        len(combined_api["paths"])
    )

    return combined_api


@app.api_route(
    "/{service}/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS"
    ],
    include_in_schema=False
)
async def proxy(
    service: str,
    path: str,
    request: Request
):

    if service not in SERVICES:

        return Response(
            content='{"detail":"Service not found"}',
            status_code=404,
            media_type="application/json"
        )

    service_url = SERVICES[service].replace(
        "/openapi.json",
        ""
    )

    target_url = f"{service_url}/{path}"

    if request.url.query:

        target_url += (
            f"?{request.url.query}"
        )

    body = await request.body()

    headers = dict(request.headers)

    headers.pop(
        "host",
        None
    )

    try:

        response = requests.request(

            method=request.method,

            url=target_url,

            headers=headers,

            data=body,

            timeout=60
        )

        excluded_headers = {
            "content-encoding",
            "transfer-encoding",
            "connection"
        }

        response_headers = {

            key: value

            for key, value in response.headers.items()

            if key.lower()
            not in excluded_headers
        }

        return Response(

            content=response.content,

            status_code=response.status_code,

            headers=response_headers,

            media_type=response.headers.get(
                "content-type"
            )
        )

    except requests.RequestException as exc:

        print(
            "Proxy error:",
            exc
        )

        return Response(

            content='{"detail":"Service unavailable"}',

            status_code=502,

            media_type="application/json"
        )


@app.get(
    "/scalar",
    include_in_schema=False
)
def scalar():

    return get_scalar_api_reference(

        openapi_url="/openapi.json",

        title="Hair Salon Blog System API"

    )


@app.get(
    "/",
    include_in_schema=False
)
def root():

    return {

        "message":
        "Hair Salon Blog System API",

        "scalar":
        "/scalar",

        "services": {

            "user":
            "http://127.0.0.1:7000",

            "blog":
            "http://127.0.0.1:7002",

            "gallery":
            "http://127.0.0.1:7001",

            "file":
            "http://127.0.0.1:7006",

            "comment":
            "http://127.0.0.1:7005",

            "tag":
            "http://127.0.0.1:7007",

            "category":
            "http://127.0.0.1:7008",

          "aggregation": "http://127.0.0.1:7009"

        }
    }
