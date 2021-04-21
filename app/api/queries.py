"""
Query resolvers
"""
from ariadne import QueryType, ObjectType  # type: ignore
from ariadne.types import GraphQLResolveInfo  # type: ignore
from app.db.base import get_db
import app.db.models as models
import app.db.crud as crud
from app.auth import Auth

query = QueryType()
me_type = ObjectType("Me")
item_type = ObjectType("Item")


@query.field("me")
def resolve_me(unused, info: GraphQLResolveInfo, **_):
    del unused

    with get_db() as db:
        auth = Auth.from_info(info=info, db=db)
        if auth.user is None:
            raise ValueError("Not logged in")
        return auth.user


@me_type.field("items")
def resolve_my_items(parent: models.User, unused, **_):
    del unused
    with get_db() as db:
        return crud.get_items_by_owner_id(db=db, ownerId=parent.id)


@query.field("items")
def resolve_items(*_, **kwargs):
    filters = kwargs.get("filter", {})
    with get_db() as db:
        return crud.get_items(db=db, **filters)


@item_type.field("owner")
def resolve_item_owner(parent: models.Item, unused, **_):
    del unused
    with get_db() as db:
        return crud.get_user_by_id(db=db, id=parent.ownerId)


queries = (query, me_type, item_type)
