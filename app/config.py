"""Global config: default config -> environment vars"""
import os
import logging

# app
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = os.environ.get("PORT", "8000")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "info")
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "SQLALCHEMY_DATABASE_URI", "postgresql://postgres@localhost/main"
)

# auth
AUTH_SECRET_KEY = "<my-secret-key>"
AUTH_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 12


_prot, _rest = SQLALCHEMY_DATABASE_URI.split("://")
_creds, _rest = _rest.split("@")

_log = logging.getLogger(__name__)
_log.info("HOST: %s", HOST)
_log.info("PORT: %s", PORT)
_log.info("SQLALCHEMY_DATABASE_URI: %s://%s", _prot, _rest)
_log.info("AUTH_SECRET_KEY: %s", AUTH_SECRET_KEY)
_log.info("AUTH_ALGORITHM: %s", AUTH_ALGORITHM)
_log.info("ACCESS_TOKEN_EXPIRE_MINUTES: %s", ACCESS_TOKEN_EXPIRE_MINUTES)
