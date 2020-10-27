"""App entrypoint"""
import logging
from fastapi import FastAPI
from starlette.requests import Request  # type: ignore
from starlette.middleware.cors import CORSMiddleware  # type: ignore
from ariadne.asgi import GraphQL  # type: ignore
from app.schema import SCHEMA
from app.config import SQLALCHEMY_DATABASE_URI, VERSION

descr = f"""
Main description...

Find GraphiQL under `/`.

DB connection: `{SQLALCHEMY_DATABASE_URI}`
"""

log = logging.getLogger(__name__)

app = FastAPI(title="My GraphQL API", description=descr, version=VERSION)
app.mount("/", GraphQL(schema=SCHEMA))


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
