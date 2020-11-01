"""
Declarative Base for SQLAlchemy

Declaring declarative base for SQLAlchemy and creating a contect manager
for getting a database session.

graphene: Queries are somehow magically generated when declaring the database
model on graphene_sqlalchemy objects. For mutations I need to explicitly use
the database session. That's what the context manager is for.

alembic: alembic's env.py needs the declarative base for `target_metadata = Base.metadata`.
Dont forget to also import the actual model definitions after importing the declarative
base in env.py.
"""
from contextlib import contextmanager
from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from sqlalchemy.orm import sessionmaker, scoped_session  # type: ignore
from app.config import SQLALCHEMY_DATABASE_URI

engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionFact = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


@contextmanager
def get_db():
    db = SessionFact()
    try:
        yield db
    finally:
        db.close()
