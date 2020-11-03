"""Find GraphiQL under `/`"""
from pathlib import Path
from typing import Callable, Any
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware  # type: ignore
from starlette.middleware.authentication import AuthenticationMiddleware  # type: ignore
from ariadne import load_schema_from_path, make_executable_schema  # type: ignore
from ariadne.asgi import GraphQL  # type: ignore
from ariadne.types import GraphQLResolveInfo  # type: ignore
from app.api.resolvers import OBJ_TYPES
from app.config import VERSION
from app.auth import Auth

# TODO: implement some tests
# TODO: test if whole auth/filter fields is easier in ariadne

_schema = load_schema_from_path(str(Path("app") / "api"))


def test_middleware(
    resolver: Callable, obj: Any, info: GraphQLResolveInfo, **kwargs
) -> Any:
    print("before resolve")
    res = resolver(obj, info, **kwargs)
    print("after resolve")
    return res


# TODO: das hier geht an für sich -> starlette und fastAPI Sachen wegwerfen
def auth_middleware(resolver, obj, info, **kwargs):
    context = info.context
    headers = context["request"].headers
    context["auth"] = Auth(auth=headers.get("Authorization"))
    return resolver(obj, info, **kwargs)


app = GraphQL(
    make_executable_schema(_schema, *OBJ_TYPES), middleware=[auth_middleware],  # type: ignore
)

# app = FastAPI(title="My GraphQL API", description=__doc__, version=VERSION)
# app.mount("/", GraphQL(schema=make_executable_schema(_schema, *OBJ_TYPES)))

# CORS
# app.add_middleware(
#    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
# )

# Auth
# app.add_middleware(AuthenticationMiddleware, backend=AuthBackend())
