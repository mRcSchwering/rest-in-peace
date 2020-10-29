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
from ariadne import QueryType, MutationType, ObjectType, ScalarType  # type: ignore
from ariadne.types import GraphQLResolveInfo  # type: ignore
from app.db.base import get_db
import app.db.models as models
import app.db.crud as crud

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
def resolve_users(parent: Any, info: GraphQLResolveInfo, **kwargs) -> List[models.User]:
    with get_db() as db:
        return crud.read_users(db=db, **kwargs.get("filter", {}))


@mutation.field("createUser")
def resolve_create_user(parent: Any, info: GraphQLResolveInfo, **kwargs) -> dict:
    with get_db() as db:
        return crud.create_user(db=db, **kwargs["input"])


@mutation.field("updateUser")
def resolve_update_user(parent: Any, info: GraphQLResolveInfo, **kwargs) -> dict:
    with get_db() as db:
        return crud.update_user(db=db, **kwargs["input"])


@user.field("items")
def resolve_items(
    owner: models.User, info: GraphQLResolveInfo, **kwargs
) -> List[models.Item]:
    with get_db() as db:
        return crud.read_items(db=db, owner_dbid=owner.dbid)


@mutation.field("createItem")
def resolve_create_item(parent: Any, info: GraphQLResolveInfo, **kwargs) -> dict:
    with get_db() as db:
        return crud.create_item(db=db, **kwargs["input"])


@mutation.field("updateItem")
def resolve_update_item(parent: Any, info: GraphQLResolveInfo, **kwargs) -> dict:
    with get_db() as db:
        return crud.update_item(db=db, **kwargs["input"])


OBJ_TYPES = [query, mutation, user, date_scalar]

