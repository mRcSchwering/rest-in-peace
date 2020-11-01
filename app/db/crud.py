"""Create, read, update, delete"""
from typing import List, Union
import datetime as dt
from sqlalchemy.orm import Session  # type: ignore
from app.db import models


def _get_payload(error: Union[None, str] = None, obj: Union[dict, None] = None) -> dict:
    out = {"status": True if error is None else False, "error": error}
    if obj is not None:
        out.update(obj)
    return out


def read_users(
    db: Session,
    name_like: Union[str, None] = None,
    email_is: Union[str, None] = None,
    dbid_is: Union[str, None] = None,
) -> List[models.User]:
    query = db.query(models.User)
    if name_like is not None:
        query = query.filter(models.User.name.ilike(f"%{name_like}%"))
    if email_is is not None:
        query = query.filter(models.User.email == email_is)
    if dbid_is is not None:
        query = query.filter(models.User.dbid == dbid_is)
    return query.all()


def get_user_by_email(db: Session, email: str) -> Union[models.User, None]:
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, email: str, name: str, hashed_password: str) -> dict:
    db_obj = db.query(models.User).filter(models.User.email == email).first()
    if db_obj is not None:
        return _get_payload(error="user exists")
    db_obj = models.User(
        name=name, email=email, hashed_password=hashed_password, is_active=True,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return _get_payload(obj={"user": db_obj})


def update_user(
    db: Session,
    email: Union[str, None] = None,
    name: Union[str, None] = None,
    hashed_password: Union[str, None] = None,
) -> dict:
    db_obj = db.query(models.User).filter(models.User.email == email).first()
    if db_obj is None:
        return _get_payload(error="user doesnt exist")

    if hashed_password is not None:
        db_obj.hashed_password = hashed_password
    if name is not None:
        db_obj.name = name
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return _get_payload(obj={"user": db_obj})


def read_items(db: Session, **kwarg_filters) -> List[models.Item]:
    res = db.query(models.Item).filter_by(**kwarg_filters)
    return res.all()


def create_item(
    db: Session,
    owner_dbid: int,
    title: Union[None, str] = None,
    description: Union[str, None] = None,
) -> dict:
    """Create new item for owner"""
    today = dt.datetime.now().date()
    db_owner = db.query(models.User).filter(models.User.dbid == owner_dbid).first()
    if db_owner is None:
        return _get_payload(error="owner_dbid doesnt exist")
    db_obj = models.Item(
        title=title, description=description, owner_dbid=owner_dbid, posted_on=today
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return _get_payload(obj={"item": db_obj})


def update_item(
    db: Session,
    dbid: int,
    title: Union[None, str] = None,
    description: Union[str, None] = None,
) -> dict:
    """Update existing item based on dbid"""
    db_obj = db.query(models.Item).filter(models.Item.dbid == dbid).first()
    if db_obj is None:
        return _get_payload(error="item doesnt exist")
    if title is not None:
        db_obj.title = title
    if description is not None:
        db_obj.description = description
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return _get_payload(obj={"item": db_obj})
