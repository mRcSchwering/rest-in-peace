"""App entrypoint"""
import logging
from pathlib import Path
from fastapi import FastAPI
from starlette.requests import Request  # type: ignore
from starlette.middleware.cors import CORSMiddleware  # type: ignore
from ariadne import load_schema_from_path, make_executable_schema  # type: ignore
from ariadne.asgi import GraphQL  # type: ignore
from app.api.resolvers import OBJ_TYPES
from app.config import SQLALCHEMY_DATABASE_URI, VERSION

# TODO: setup auth
# TODO: revisit docker images
# TODO: implement some tests

_WEB_INFO = f"""
Main description...

Find GraphiQL under `/`.

DB connection: `{SQLALCHEMY_DATABASE_URI}`
"""

_SCHEMA = load_schema_from_path(str(Path("app") / "api"))

log = logging.getLogger(__name__)

app = FastAPI(title="My GraphQL API", description=_WEB_INFO, version=VERSION)
app.mount("/", GraphQL(schema=make_executable_schema(_SCHEMA, *OBJ_TYPES)))


# CORS middleware
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


@app.middleware("http")
async def some_bullshit(request: Request, call_next):
    log.info("Im a middleware")
    try:
        response = await call_next(request)
    finally:
        log.info("Im done")
    return response
