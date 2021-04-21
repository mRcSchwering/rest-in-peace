"""ASGI app. Serves a GraphQL playground on '/'"""
from pathlib import Path
from starlette.middleware.cors import CORSMiddleware  # type: ignore
from ariadne import load_schema_from_path, make_executable_schema  # type: ignore
from ariadne.asgi import GraphQL  # type: ignore
from app.api.queries import queries
from app.api.mutations import mutations
from app.api.types import types
from app.api.directives import directives


_schema_str = load_schema_from_path(str(Path("app") / "api"))
_schema = make_executable_schema(
    _schema_str, *queries, *mutations, *types, directives=directives
)

app = CORSMiddleware(
    GraphQL(_schema),  # type: ignore
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
