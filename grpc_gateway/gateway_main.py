
from copy import deepcopy

import requests
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from routes.aggregation import router as aggregation_router


app = FastAPI(
    title="Hair Salon Blog gRPC System API",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(aggregation_router)


SERVICES = {
    "User": {
        "name": "user service",
        "url": "http://127.0.0.1:7000",
    },
    "Gallery": {
        "name": "gallery service",
        "url": "http://127.0.0.1:7001",
    },
    "Blog": {
        "name": "blog service",
        "url": "http://127.0.0.1:7002",
    },
    "File": {
        "name": "file service",
        "url": "http://127.0.0.1:7006",
    },
    "Comment": {
        "name": "comment service",
        "url": "http://127.0.0.1:7005",
    },
    "Tag": {
        "name": "tag service",
        "url": "http://127.0.0.1:7007",
    },
    "Category": {
        "name": "category service",
        "url": "http://127.0.0.1:7008",
    },
}


def rewrite_refs(data, prefix):
    """Rewrite local OpenAPI component references."""

    if isinstance(data, dict):
        result = {}

        for key, value in data.items():
            if key == "$ref" and isinstance(value, str):
                component_prefix = "#/components/"

                if value.startswith(component_prefix):
                    parts = value.split("/")

                    if len(parts) >= 4:
                        parts[3] = f"{prefix}_{parts[3]}"
                        value = "/".join(parts)

                result[key] = value

            elif key == "security" and isinstance(value, list):
                result[key] = [
                    {
                        f"{prefix}_{scheme}": scopes
                        for scheme, scopes in requirement.items()
                    }
                    for requirement in value
                ]

            else:
                result[key] = rewrite_refs(value, prefix)

        return result

    if isinstance(data, list):
        return [rewrite_refs(item, prefix) for item in data]

    return data


def build_openapi():
    combined = {
        "openapi": "3.1.0",
        "info": {
            "title": "Hair Salon Blog gRPC System API",
            "version": "1.0.0",
            "description": (
                "Unified API documentation for User, Blog, Gallery, "
                "File, Comment, Tag, Category and Aggregation services."
            ),
        },
        "paths": {},
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "Enter your JWT access token.",
                }
            }
        },
        "tags": [],
        "security": [
            {"BearerAuth": []}
        ],
    }

    for service_key, service in SERVICES.items():
        openapi_url = f"{service['url']}/openapi.json"

        try:
            response = requests.get(
                openapi_url,
                timeout=10,
            )
            response.raise_for_status()
            spec = response.json()

        except (requests.RequestException, ValueError) as exc:
            raise HTTPException(
                status_code=503,
                detail=(
                    f"{service['name']} OpenAPI is unavailable. "
                    f"URL: {openapi_url}. Error: {exc}"
                ),
            ) from exc

        service_paths = spec.get("paths", {})

        if not isinstance(service_paths, dict):
            raise HTTPException(
                status_code=502,
                detail=f"Invalid OpenAPI paths from {service['name']}.",
            )

        for path, path_item in service_paths.items():
            new_path = f"/{service_key}{path}"

            combined["paths"][new_path] = rewrite_refs(
                deepcopy(path_item),
                service_key,
            )

            for method, operation in combined["paths"][new_path].items():
                if method.lower() not in {
                    "get",
                    "post",
                    "put",
                    "patch",
                    "delete",
                    "options",
                    "head",
                    "trace",
                }:
                    continue

                if not isinstance(operation, dict):
                    continue

                if "tags" in operation:
                    operation["tags"] = [
                        f"{service['name']} - {tag}"
                        for tag in operation["tags"]
                    ]
                else:
                    operation["tags"] = [service["name"]]

                operation["x-original-path"] = path

                # مسیرهای ورود و ثبت‌نام کاربر بدون JWT
                if (
                    service_key == "User"
                    and path.rstrip("/") in {
                        "/users/login",
                        "/users/register",
                    }
                ):
                    operation["security"] = []
                else:
                    operation["security"] = [
                        {"BearerAuth": []}
                    ]

        # ادغام components
        for section, items in spec.get("components", {}).items():
            if not isinstance(items, dict):
                continue

            if section == "securitySchemes":
                continue

            combined["components"].setdefault(section, {})

            for name, component in items.items():
                new_name = f"{service_key}_{name}"

                combined["components"][section][new_name] = rewrite_refs(
                    deepcopy(component),
                    service_key,
                )

        # ادغام tagها
        for tag in spec.get("tags", []):
            tag_name = tag.get("name")

            if tag_name:
                combined["tags"].append({
                    "name": f"{service['name']} - {tag_name}",
                    "description": tag.get("description", ""),
                })

    # مستندات مسیر Aggregation
    combined["paths"]["/aggregation/blogs/{blog_id}"] = {
        "get": {
            "tags": ["Aggregation"],
            "summary": "Get aggregated blog and user",
            "description": (
                "Returns blog and user information from the "
                "Aggregation gRPC service."
            ),
            "operationId": "get_aggregated_blog",
            "parameters": [
                {
                    "name": "blog_id",
                    "in": "path",
                    "required": True,
                    "description": "ID of the blog",
                    "schema": {
                        "type": "integer",
                    },
                }
            ],
            "responses": {
                "200": {
                    "description": "Aggregated blog and user",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "blog": {
                                        "type": "object",
                                    },
                                    "user": {
                                        "type": "object",
                                    },
                                },
                            }
                        }
                    },
                },
                "502": {
                    "description": "Aggregation gRPC error",
                },
            },
        }
    }

    combined["tags"].append({
        "name": "Aggregation",
        "description": "Aggregated responses from gRPC services",
    })

    if not combined["paths"]:
        raise HTTPException(
            status_code=502,
            detail=(
                "No paths were found in the OpenAPI documents. "
                "Check the individual gateways."
            ),
        )

    return combined


@app.get("/openapi.json", include_in_schema=False)
def unified_openapi():
    return build_openapi()


@app.get("/scalar", include_in_schema=False)
def scalar_docs():
    return get_scalar_api_reference(
        openapi_url="/openapi.json",
        title="Hair Salon Blog gRPC System API - Unified Scalar",
    )


@app.get("/", include_in_schema=False)
def home():
    return {
        "message": "Unified gRPC Gateway Documentation",
        "scalar": "/scalar",
        "openapi": "/openapi.json",
        "services": {
            key: service["url"]
            for key, service in SERVICES.items()
        },
        "aggregation": "/aggregation/blogs/{blog_id}",
    }


@app.api_route(
    "/{service}/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    include_in_schema=False,
)
async def proxy(service: str, path: str, request: Request):
    if service not in SERVICES:
        raise HTTPException(
            status_code=404,
            detail="Service not found",
        )

    target_url = f"{SERVICES[service]['url']}/{path}"

    if request.url.query:
        target_url += f"?{request.url.query}"

    body = await request.body()

    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in {
            "host",
            "content-length",
            "connection",
        }
    }

    try:
        response = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=body,
            timeout=60,
        )

        excluded_headers = {
            "content-encoding",
            "transfer-encoding",
            "connection",
            "content-length",
        }

        response_headers = {
            key: value
            for key, value in response.headers.items()
            if key.lower() not in excluded_headers
        }

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=response_headers,
            media_type=response.headers.get("content-type"),
        )

    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=f"{service} Gateway request failed: {exc}",
        ) from exc
