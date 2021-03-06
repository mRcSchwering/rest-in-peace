"""
Database schema

alembic: alembic's env.py needs the declarative base for `target_metadata = Base.metadata`.
Dont forget to also import this model definition after importing the declarative
base in env.py.
"""
from sqlalchemy import Column, ForeignKey, Integer, String, Text, Boolean, Date  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashedPassword = Column(String, nullable=False)
    isActive = Column(Boolean, default=True)
    isSuperuser = Column(Boolean, default=False)

    items = relationship("Item", backref="owner")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    postedOn = Column(Date, nullable=False)

    ownerId = Column(Integer, ForeignKey("users.id"), nullable=False)
