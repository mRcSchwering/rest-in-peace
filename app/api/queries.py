"""
Query resolvers

Get selected fields from GraphQLResolveInfo, example:

    load_items = False
    if info.field_nodes[0].selection_set is not None:
        for node in info.field_nodes[0].selection_set.selections:
            a_field = node.name.value
"""
from typing import List, Union
from ariadne import QueryType, ObjectType  # type: ignore
from ariadne.types import GraphQLResolveInfo  # type: ignore
from app.db.base import get_db
import app.db.models as models
import app.db.crud as crud
from app.auth import Auth

query = QueryType()
user_type = ObjectType("User")
item_type = ObjectType("Item")


@query.field("me")
def resolve_me(unused, info: GraphQLResolveInfo, **_) -> Union[None, models.User]:
    del unused
    auth: Auth = info.context["auth"]
    if auth.user is not None:
        with get_db() as db:
            return crud.get_user_by_email(db=db, email=auth.user.email)
    return None


@query.field("users")
def resolve_users(*_, **kwargs) -> List[models.User]:
    filters = kwargs.get("filter", {})
    with get_db() as db:
        return crud.read_users(db=db, **filters)


@user_type.field("items")
def resolve_user_items(owner: models.User, **kwargs) -> List[models.Item]:
    filters = kwargs.get("filter", {})
    filters["dbid_is"] = owner.dbid
    with get_db() as db:
        return crud.read_items(db=db, **filters)


@query.field("items")
def resolve_items(*_, **kwargs) -> List[models.Item]:
    filters = kwargs.get("filter", {})
    with get_db() as db:
        return crud.read_items(db=db, **filters)


@item_type.field("owner")
def resolve_item_owner(item: models.Item, _, **kwargs) -> models.User:
    filters = kwargs.get("filter", {})
    filters["dbid_is"] = item.owner_dbid
    with get_db() as db:
        return crud.read_users(db=db, **filters)[0]


queries = (query, user_type, item_type)
