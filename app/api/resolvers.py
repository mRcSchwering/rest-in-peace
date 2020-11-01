"""
GraphQL definitions


getting selected fields from info, example:

    load_items = False
    if info.field_nodes[0].selection_set is not None:
        for node in info.field_nodes[0].selection_set.selections:
            a_field = node.name.value
"""
from typing import Any, List
import datetime as dt
from starlette.requests import Request  # type: ignore
from ariadne import QueryType, MutationType, ObjectType, ScalarType  # type: ignore
from ariadne.types import GraphQLResolveInfo  # type: ignore
from app.db.base import get_db
import app.db.models as models
import app.db.crud as crud
from app.auth import (
    password_matches,
    create_access_token,
    TokenData,
    TokenValidationFailed,
    hash_password,
)

query = QueryType()
mutation = MutationType()
user = ObjectType("User")
date_scalar = ScalarType("Date")


@date_scalar.serializer
def serialize_datetime(d: dt.date) -> str:
    return d.strftime("%Y-%m-%d")


@date_scalar.value_parser
def parse_datetime_value(d: str) -> dt.date:
    return dt.datetime.strptime(d, "%Y-%m-%d").date()


@query.field("users")
def resolve_users(_, info: GraphQLResolveInfo, **kwargs) -> List[models.User]:
    print("in resolver")
    request: Request = info.context["request"]
    print(
        f"request user {request.user.display_name}, auth?: {request.user.is_authenticated}"
    )
    with get_db() as db:
        return crud.read_users(db=db, **kwargs.get("filter", {}))


@mutation.field("login")
def resolve_login(*_, **kwargs):
    with get_db() as db:
        db_user = crud.get_user_by_email(db=db, email=kwargs["input"]["email"])

    if db_user is None or not password_matches(
        plain=kwargs["input"]["password"], hashed=db_user.hashed_password
    ):
        return {"status": False, "error": "email or password wrong"}

    data = TokenData(username=db_user.name, scopes=["authenticated"])
    try:
        token = create_access_token(token_data=data)
    except TokenValidationFailed:
        return {"status": False, "error": "token validation failed"}
    return {"status": True, "token": token}


@mutation.field("createUser")
def resolve_create_user(*_, **kwargs) -> dict:
    email = kwargs["input"]["email"]
    name = kwargs["input"]["name"]
    hashed_password = hash_password(kwargs["input"]["password"])
    with get_db() as db:
        return crud.create_user(
            db=db, email=email, name=name, hashed_password=hashed_password
        )


@mutation.field("updateUser")
def resolve_update_user(*_, **kwargs) -> dict:
    email = kwargs["input"]["email"]
    name = kwargs["input"]["name"]
    hashed_password = hash_password(kwargs["input"]["password"])
    with get_db() as db:
        return crud.update_user(
            db=db, email=email, name=name, hashed_password=hashed_password
        )


@user.field("items")
def resolve_items(
    owner: models.User, info: GraphQLResolveInfo, **kwargs
) -> List[models.Item]:
    with get_db() as db:
        return crud.read_items(db=db, owner_dbid=owner.dbid)


@mutation.field("createItem")
def resolve_create_item(_, info: GraphQLResolveInfo, **kwargs) -> dict:
    with get_db() as db:
        return crud.create_item(db=db, **kwargs["input"])


@mutation.field("updateItem")
def resolve_update_item(_, info: GraphQLResolveInfo, **kwargs) -> dict:
    with get_db() as db:
        return crud.update_item(db=db, **kwargs["input"])


OBJ_TYPES = [query, mutation, user, date_scalar]

