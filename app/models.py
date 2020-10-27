"""
Database schema

alembic: alembic's env.py needs the declarative base for `target_metadata = Base.metadata`.
Dont forget to also import this model definition after importing the declarative
base in env.py.
"""
from sqlalchemy import Column, ForeignKey, Integer, String, Text, Boolean  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore
from app.db import Base


class User(Base):
    __tablename__ = "users"

    dbid = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    items = relationship("Item", backref="owner")


class Item(Base):
    __tablename__ = "items"

    dbid = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)

    owner_dbid = Column(Integer, ForeignKey("users.dbid"), nullable=False)
