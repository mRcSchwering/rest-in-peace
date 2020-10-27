"""Create, read, update, delete"""
from typing import List
from sqlalchemy.orm import Session, joinedload  # type: ignore
from app import models


def read_users(
    db: Session, load_items: bool = False, **kwarg_filters
) -> List[models.User]:
    query = db.query(models.User).filter_by(**kwarg_filters)
    if load_items:
        query = query.options(joinedload("items"))
    return query.all()


def read_items(db: Session, **kwarg_filters) -> List[models.Item]:
    res = db.query(models.Item).filter_by(**kwarg_filters)
    return res.all()

