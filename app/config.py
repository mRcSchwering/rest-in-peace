"""Global config: default config -> environment vars"""
import os

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = os.environ.get("PORT", "8000")
VERSION = os.environ.get("VERSION", "development")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "info")
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "SQLALCHEMY_DATABASE_URI", "postgresql://postgres@localhost/main"
)
