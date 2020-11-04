"""Find GraphiQL under `/`"""
from pathlib import Path
from starlette.middleware.cors import CORSMiddleware  # type: ignore
from ariadne import load_schema_from_path, make_executable_schema  # type: ignore
from ariadne.asgi import GraphQL  # type: ignore
from app.auth import Auth
from app.api.queries import queries
from app.api.mutations import mutations
from app.api.types import types
from app.api.directives import directives


_schema_str = load_schema_from_path(str(Path("app") / "api"))
_schema = make_executable_schema(
    _schema_str, *queries, *mutations, *types, directives=directives
)


def auth_middleware(resolver, obj, info, **kwargs):
    """Add authentication to context"""
    context = info.context
    headers = context["request"].headers
    context["auth"] = Auth(auth=headers.get("Authorization"))
    return resolver(obj, info, **kwargs)


app = CORSMiddleware(
    GraphQL(_schema, middleware=[auth_middleware]),  # type: ignore
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
