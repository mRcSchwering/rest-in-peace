"""
Mutation resolvers
"""
from typing import Any, Dict, Optional
from ariadne import MutationType  # type: ignore
from app.exceptions import NotFound, Exists
from app.db.base import get_db
import app.db.crud as crud
from app.auth import password_matches, create_access_token, hash_password

mutation = MutationType()


class Payload:
    """
    Mutation resolver payload with `status`, `error` and object(s).

    Args:
        error: opt error message (will set `status = False`)
        objs: dict of object name - object
    """

    def __init__(
        self, error: Optional[str] = None, objs: Optional[Dict[str, Any]] = None
    ):
        self.status = True if error is None else False
        self.error = error
        if objs is not None:
            for k, d in objs.items():
                setattr(self, k, d)


@mutation.field("login")
def resolve_login(*_, **kwargs) -> Payload:
    email = kwargs["input"]["email"]
    password = kwargs["input"]["password"]
    with get_db() as db:
        db_user = crud.get_user_by_email(db=db, email=email)

    if db_user is None or not password_matches(
        plain=password, hashed=db_user.hashed_password
    ):
        return Payload(error="email or password wrong")

    token = create_access_token(username=db_user.email)
    return Payload(objs={"token": token})


@mutation.field("createUser")
def resolve_create_user(*_, **kwargs) -> Payload:
    email = kwargs["input"]["email"]
    name = kwargs["input"]["name"]
    hashed_password = hash_password(kwargs["input"]["password"])
    with get_db() as db:
        try:
            db_user = crud.create_user(
                db=db, email=email, name=name, hashed_password=hashed_password
            )
        except Exists as err:
            return Payload(error=str(err))
    return Payload(objs={"user": db_user})


@mutation.field("updateUser")
def resolve_update_user(*_, **kwargs) -> Payload:
    email = kwargs["input"]["email"]
    name = kwargs["input"]["name"]
    hashed_password = hash_password(kwargs["input"]["password"])
    with get_db() as db:
        try:
            db_user = crud.update_user(
                db=db, email=email, name=name, hashed_password=hashed_password
            )
        except NotFound as err:
            return Payload(error=str(err))
    return Payload(objs={"user": db_user})


@mutation.field("createItem")
def resolve_create_item(*_, **kwargs) -> Payload:
    with get_db() as db:
        try:
            db_item = crud.create_item(db=db, **kwargs["input"])
        except NotFound as err:
            return Payload(error=str(err))
    return Payload(objs={"item": db_item})


@mutation.field("updateItem")
def resolve_update_item(*_, **kwargs) -> Payload:
    with get_db() as db:
        try:
            db_item = crud.update_item(db=db, **kwargs["input"])
        except NotFound as err:
            return Payload(error=str(err))
    return Payload(objs={"item": db_item})


mutations = (mutation,)

