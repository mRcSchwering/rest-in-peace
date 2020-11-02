"""
GraphQL definitions



Get selected fields from GraphQLResolveInfo, example:

    load_items = False
    if info.field_nodes[0].selection_set is not None:
        for node in info.field_nodes[0].selection_set.selections:
            a_field = node.name.value
"""
from typing import Any, List, Dict, Optional
import datetime as dt
from ariadne import QueryType, MutationType, ObjectType, ScalarType  # type: ignore
from ariadne.types import GraphQLResolveInfo  # type: ignore
from app.exceptions import NotFound, Exists
from app.db.base import get_db
import app.db.models as models
import app.db.crud as crud
from app.auth import (
    password_matches,
    create_access_token,
    TokenData,
    hash_password,
    Auth,
)

query = QueryType()
mutation = MutationType()
user = ObjectType("User")
date_scalar = ScalarType("Date")


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


@date_scalar.serializer
def serialize_datetime(d: dt.date) -> str:
    return d.strftime("%Y-%m-%d")


@date_scalar.value_parser
def parse_datetime_value(d: str) -> dt.date:
    return dt.datetime.strptime(d, "%Y-%m-%d").date()


@query.field("users")
def resolve_users(_, info: GraphQLResolveInfo, **kwargs) -> List[models.User]:
    auth: Auth = info.context["request"].user
    filters = kwargs.get("filter", {})
    with get_db() as db:
        return crud.read_users(db=db, sess_user=auth.user, **filters)


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

    data = TokenData(username=db_user.name, scopes=["authenticated"])
    token = create_access_token(token_data=data)
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


@user.field("items")
def resolve_items(
    owner: models.User, info: GraphQLResolveInfo, **kwargs
) -> List[models.Item]:
    auth: Auth = info.context["request"].user
    with get_db() as db:
        return crud.read_items(db=db, sess_user=auth.user, owner_dbid=owner.dbid)


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


OBJ_TYPES = [query, mutation, user, date_scalar]

