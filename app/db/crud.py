"""Create, read, update, delete in database"""
from typing import List, Union
import datetime as dt
from sqlalchemy.orm import Session  # type: ignore
from app.exceptions import Exists, NotFound
from app.db import models


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
    db_objs = query.all()
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
    db: Session,
    dbid_is: Union[int, None] = None,
    title_like: Union[str, None] = None,
    description_like: Union[str, None] = None,
) -> List[models.Item]:
    query = db.query(models.Item)
    if dbid_is is not None:
        query = query.filter(models.Item.dbid == dbid_is)
    if title_like is not None:
        query = query.filter(models.Item.title.ilike(f"%{title_like}%"))
    if description_like is not None:
        query = query.filter(models.Item.description.ilike(f"%{description_like}%"))
    return query.all()


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
