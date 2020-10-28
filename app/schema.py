"""
GraphQL definitions


getting selected fields from info, example:

    load_items = False
    if info.field_nodes[0].selection_set is not None:
        for node in info.field_nodes[0].selection_set.selections:
            a_field = node.name.value
"""
from typing import Any, List
from ariadne import QueryType, MutationType, ObjectType, ScalarType, make_executable_schema  # type: ignore
from ariadne.types import GraphQLResolveInfo  # type: ignore
from app.db import get_db
import app.models as models
import app.crud as crud

# TODO: implement datetime for date (with db update)
# TODO: implement interfaces for inputs and so on
# TODO: revisit filters, add sorting, pagination?

_TYPE_DEF = """
    scalar Datetime

    type Query {
        users(email: String): [User]!
    }

    type Mutation {
        createUser(input: UserInput!): UserPayload
        updateUser(input: UserInput!): UserPayload
        createItem(input: ItemInput!): ItemPayload
        updateItem(input: ItemUpdateInput!): ItemPayload
    }

    input UserInput {
        name: String!
        email: String!
        password: String!
    }

    type UserPayload {
        status: Boolean!
        error: String
        user: User
    }

    type User {
        dbid: Int!
        name: String!
        email: String!
        is_active: Boolean
        is_superuser: Boolean
        items: [Item]
    }

    input ItemInput {
        owner_dbid: Int!
        title: String!
        description: String
        posted_on: Datetime
    }

    input ItemUpdateInput {
        dbid: Int!
        title: String
        description: String
    }

    type ItemPayload {
        status: Boolean!
        error: String
        item: Item
    }

    type Item {
        dbid: Int!
        title: String
        description: String
    }
"""

query = QueryType()
mutation = MutationType()
user = ObjectType("User")
datetime_scalar = ScalarType("Datetime")


@datetime_scalar.serializer
def serialize_datetime(value):
    """ääääääääääääääääää"""
    return value.isoformat()


@datetime_scalar.value_parser
def parse_datetime_value(value):
    """jöööööööööööööööööööööö"""
    return value


@query.field("users")
def resolve_users(parent: Any, info: GraphQLResolveInfo, **kwargs) -> List[models.User]:
    with get_db() as db:
        return crud.read_users(db=db, **kwargs)


@mutation.field("createUser")
def resolve_create_user(
    parent: Any, info: GraphQLResolveInfo, **kwargs
) -> crud.UserPayload:
    with get_db() as db:
        return crud.create_user(db=db, **kwargs["input"])


@mutation.field("updateUser")
def resolve_update_user(
    parent: Any, info: GraphQLResolveInfo, **kwargs
) -> crud.UserPayload:
    with get_db() as db:
        return crud.update_user(db=db, **kwargs["input"])


@user.field("items")
def resolve_items(
    owner: models.User, info: GraphQLResolveInfo, **kwargs
) -> List[models.Item]:
    with get_db() as db:
        return crud.read_items(db=db, owner_dbid=owner.dbid)


@mutation.field("createItem")
def resolve_create_item(
    parent: Any, info: GraphQLResolveInfo, **kwargs
) -> crud.ItemPayload:
    with get_db() as db:
        return crud.create_item(db=db, **kwargs["input"])


@mutation.field("updateItem")
def resolve_update_item(
    parent: Any, info: GraphQLResolveInfo, **kwargs
) -> crud.ItemPayload:
    with get_db() as db:
        return crud.update_item(db=db, **kwargs["input"])


SCHEMA = make_executable_schema(_TYPE_DEF, query, mutation, user, datetime_scalar)

