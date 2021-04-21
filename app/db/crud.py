"""Create, read, update, delete in database"""
from typing import List, Optional
import datetime as dt
from sqlalchemy.orm import Session  # type: ignore
from app.db import models


def get_user_by_id(db: Session, id: int) -> models.User:
    return db.query(models.User).filter(models.User.id == id).first()


def get_user_by_email(db: Session, email: str) -> models.User:
    return db.query(models.User).filter(models.User.email == email).first()


def get_item_by_id(db: Session, id: int) -> models.Item:
    return db.query(models.Item).filter(models.Item.id == id).first()


def get_items_by_owner_id(db: Session, ownerId: int) -> List[models.Item]:
    return db.query(models.Item).filter(models.Item.ownerId == ownerId).all()


def get_users(db: Session, nameLike: Optional[str] = None) -> List[models.User]:
    query = db.query(models.User)
    if nameLike is not None:
        query = query.filter(models.User.name.ilike(f"%{nameLike}%"))
    return query.all()


def get_items(
    db: Session, titleLike: Optional[str] = None, descriptionLike: Optional[str] = None,
) -> List[models.Item]:
    query = db.query(models.Item)
    if titleLike is not None:
        query = query.filter(models.Item.title.ilike(f"%{titleLike}%"))
    if descriptionLike is not None:
        query = query.filter(models.Item.description.ilike(f"%{descriptionLike}%"))
    return query.all()


def create_user(
    db: Session,
    email: str,
    name: str,
    hashedPassword: str,
    isActive: bool = True,
    isSuperuser: bool = False,
    **_,
) -> models.User:
    db_obj = db.query(models.User).filter(models.User.email == email).first()
    if db_obj is not None:
        raise ValueError(f"User with email {email} already exists")
    db_obj = models.User(
        name=name,
        email=email,
        hashedPassword=hashedPassword,
        isActive=isActive,
        isSuperuser=isSuperuser,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def create_item(
    db: Session,
    ownerId: int,
    postedOn: dt.date,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> models.Item:
    db_owner = db.query(models.User).filter(models.User.id == ownerId).first()
    if db_owner is None:
        raise ValueError(f"Owner with id {ownerId} not found")
    db_obj = models.Item(
        title=title, description=description, ownerId=ownerId, postedOn=postedOn
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_user(
    db: Session,
    user: models.User,
    name: Optional[str] = None,
    isActive: Optional[bool] = None,
    **_,
) -> models.User:
    db_obj = user

    if name is not None:
        db_obj.name = name
    if isActive is not None:
        db_obj.isActive = isActive

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_item(
    db: Session,
    ownerId: int,
    itemId: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    postedOn: Optional[dt.date] = None,
    **_,
) -> models.Item:
    db_obj = get_item_by_id(db=db, id=itemId)
    if db_obj is None:
        raise ValueError(f"Item with id {itemId} doesnt exist")
    if db_obj.ownerId != ownerId:
        raise ValueError(f"Item with id {itemId} does not belong to you")

    if title is not None:
        db_obj.title = title
    if description is not None:
        db_obj.description = description
    if postedOn is not None:
        db_obj.postedOn = postedOn

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_user(db: Session, id: int) -> bool:
    db_obj = get_user_by_id(db=db, id=id)
    if db_obj is None:
        raise ValueError(f"User with id {id} doesnt exist")
    db.delete(db_obj)
    db.commit()
    return True


def delete_item(db: Session, id: int) -> bool:
    db_obj = get_item_by_id(db=db, id=id)
    if db_obj is None:
        raise ValueError(f"Item with id {id} doesnt exist")
    db.delete(db_obj)
    db.commit()
    return True
