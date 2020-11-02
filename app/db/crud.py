"""Create, read, update, delete in database"""
from typing import List, Union, Optional, Dict
import datetime as dt
from sqlalchemy.orm import Session  # type: ignore
from app.exceptions import Exists, NotFound
from app.db import models

_restr_access: Dict[str, List[str]] = {
    "users": ["is_superuser", "email", "hashed_password"],
    "items": [],
}


def _filter_cols(db_objs: list, table_name: str):
    for db_obj in db_objs:
        for colname in _restr_access[table_name]:
            setattr(db_obj, colname, None)


def read_users(
    db: Session,
    name_like: Optional[str] = None,
    email_is: Optional[str] = None,
    dbid_is: Optional[str] = None,
    sess_user: Optional[models.User] = None,
) -> List[models.User]:
    query = db.query(models.User)
    if name_like is not None:
        query = query.filter(models.User.name.ilike(f"%{name_like}%"))
    if email_is is not None:
        query = query.filter(models.User.email == email_is)
    if dbid_is is not None:
        query = query.filter(models.User.dbid == dbid_is)
    db_objs = query.all()
    if sess_user is None or not sess_user.is_superuser:
        _filter_cols(db_objs=db_objs, table_name="users")
    return db_objs


def get_user_by_email(db: Session, email: str) -> Union[models.User, None]:
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(
    db: Session, email: str, name: str, hashed_password: str
) -> models.User:
    db_obj = db.query(models.User).filter(models.User.email == email).first()
    if db_obj is not None:
        raise Exists(msg="user exists")
    db_obj = models.User(
        name=name, email=email, hashed_password=hashed_password, is_active=True,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_user(
    db: Session,
    email: Union[str, None] = None,
    name: Union[str, None] = None,
    hashed_password: Union[str, None] = None,
) -> models.User:
    db_obj = db.query(models.User).filter(models.User.email == email).first()
    if db_obj is None:
        raise NotFound(msg="user doesnt exist")

    if hashed_password is not None:
        db_obj.hashed_password = hashed_password
    if name is not None:
        db_obj.name = name
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def read_items(
    db: Session, sess_user: Optional[models.User] = None, **kwarg_filters
) -> List[models.Item]:
    res = db.query(models.Item).filter_by(**kwarg_filters)
    if sess_user is None or not sess_user.is_superuser:
        _filter_cols(db_objs=res, table_name="items")
    return res.all()


def create_item(
    db: Session,
    owner_dbid: int,
    title: Union[None, str] = None,
    description: Union[str, None] = None,
) -> models.Item:
    """Create new item for owner"""
    today = dt.datetime.now().date()
    db_owner = db.query(models.User).filter(models.User.dbid == owner_dbid).first()
    if db_owner is None:
        raise NotFound(msg="owner_dbid doesnt exist")
    db_obj = models.Item(
        title=title, description=description, owner_dbid=owner_dbid, posted_on=today
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_item(
    db: Session,
    dbid: int,
    title: Union[None, str] = None,
    description: Union[str, None] = None,
) -> models.Item:
    """Update existing item based on dbid"""
    db_obj = db.query(models.Item).filter(models.Item.dbid == dbid).first()
    if db_obj is None:
        raise NotFound(msg="item doesnt exist")
    if title is not None:
        db_obj.title = title
    if description is not None:
        db_obj.description = description
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
