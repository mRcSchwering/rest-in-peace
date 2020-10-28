"""Create, read, update, delete"""
from typing import List, Union
from sqlalchemy.orm import Session  # type: ignore
from app import models


class Payload:
    def __init__(
        self, status: bool = True, error: Union[None, str] = None,
    ):
        self.status = status
        self.error = error


class UserPayload(Payload):
    def __init__(self, user: Union[None, models.User] = None, **kwargs):
        super().__init__(**kwargs)
        self.user = user


class ItemPayload(Payload):
    def __init__(self, item: Union[None, models.Item] = None, **kwargs):
        super().__init__(**kwargs)
        self.item = item


def read_users(db: Session, **kwarg_filters) -> List[models.User]:
    query = db.query(models.User).filter_by(**kwarg_filters)
    return query.all()


def create_user(db: Session, email: str, name: str, password: str) -> UserPayload:
    db_obj = db.query(models.User).filter(models.User.email == email).first()
    if db_obj is not None:
        return UserPayload(status=False, error="user exists")
    hashed_pw = "fake-hashed-" + password
    db_obj = models.User(
        name=name, email=email, hashed_password=hashed_pw, is_active=True,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return UserPayload(status=True, user=db_obj)


def update_user(
    db: Session,
    email: Union[str, None] = None,
    name: Union[str, None] = None,
    password: Union[str, None] = None,
) -> UserPayload:
    db_obj = db.query(models.User).filter(models.User.email == email).first()
    if db_obj is None:
        return UserPayload(status=False, error="user doesnt exist")

    if password is not None:
        db_obj.hashed_password = "fake-hashed-" + password
    if name is not None:
        db_obj.name = name
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return UserPayload(status=True, user=db_obj)


def read_items(db: Session, **kwarg_filters) -> List[models.Item]:
    res = db.query(models.Item).filter_by(**kwarg_filters)
    return res.all()


def create_item(
    db: Session,
    owner_dbid: int,
    title: Union[None, str] = None,
    description: Union[str, None] = None,
) -> ItemPayload:
    """Create new item for owner"""
    db_owner = db.query(models.User).filter(models.User.dbid == owner_dbid).first()
    if db_owner is None:
        return ItemPayload(status=False, error="owner_dbid doesnt exist")
    db_obj = models.Item(title=title, description=description, owner_dbid=owner_dbid)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return ItemPayload(status=True, item=db_obj)


def update_item(
    db: Session,
    dbid: int,
    title: Union[None, str] = None,
    description: Union[str, None] = None,
) -> ItemPayload:
    """Update existing item based on dbid"""
    db_obj = db.query(models.Item).filter(models.Item.dbid == dbid).first()
    if db_obj is None:
        return ItemPayload(status=False, error="item doesnt exist")
    if title is not None:
        db_obj.title = title
    if description is not None:
        db_obj.description = description
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return ItemPayload(status=True, item=db_obj)
