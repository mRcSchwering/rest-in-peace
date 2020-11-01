"""App entrypoint"""
import logging
from pathlib import Path
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware  # type: ignore
from starlette.middleware.authentication import AuthenticationMiddleware  # type: ignore
from ariadne import load_schema_from_path, make_executable_schema  # type: ignore
from ariadne.asgi import GraphQL  # type: ignore
from app.api.resolvers import OBJ_TYPES
from app.config import SQLALCHEMY_DATABASE_URI, VERSION
from app.auth import AuthBackend

# TODO: revisit docker images
# TODO: implement some tests
# TODO: use exceptions in crud instead of forming payload there?

_WEB_INFO = f"""
Main description...

Find GraphiQL under `/`.

DB connection: `{SQLALCHEMY_DATABASE_URI}`
"""

_SCHEMA = load_schema_from_path(str(Path("app") / "api"))

log = logging.getLogger(__name__)


app = FastAPI(title="My GraphQL API", description=_WEB_INFO, version=VERSION)
app.mount("/", GraphQL(schema=make_executable_schema(_SCHEMA, *OBJ_TYPES)))

# CORS
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# Auth
app.add_middleware(AuthenticationMiddleware, backend=AuthBackend())
