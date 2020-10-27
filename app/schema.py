"""
GraphQL definitions

Queries: Using the graphene_sqlalchemy magic below queries with some
useful sorting and pagination are automatically created from the
SQLAlchemy models.

Mutations: Unfortunately I have to define mutations by hand.
Arguments have to be set manually and then in the static `mutate` method
I can do whatever. The fields on the mutate class define the return object.
"""
from typing import Any, List
from ariadne import QueryType, ObjectType, make_executable_schema  # type: ignore
from ariadne.types import GraphQLResolveInfo  # type: ignore
from app.db import get_db
import app.models as models
import app.crud as crud

_TYPE_DEF = """
    type Query {
        users(email: String): [User]!
    }

    type User {
        dbid: Int!
        name: String!
        email: String!
        is_active: Boolean
        is_superuser: Boolean
        items: [Item]
    }

    type Item {
        dbid: Int!
        title: String
        description: String
    }
"""

query = QueryType()


@query.field("users")
def resolve_users(parent: Any, info: GraphQLResolveInfo, **kwargs) -> List[models.User]:
    # getting selected fields example:
    # load_items = False
    # if info.field_nodes[0].selection_set is not None:
    #     for node in info.field_nodes[0].selection_set.selections:
    #         if node.name.value == "items":  # type: ignore
    #             load_items = True

    with get_db() as db:
        return crud.read_users(db=db, **kwargs)


user = ObjectType("User")


@user.field("items")
def resolve_items(
    owner: models.User, info: GraphQLResolveInfo, **kwargs
) -> List[models.Item]:
    with get_db() as db:
        return crud.read_items(db=db, owner_dbid=owner.dbid)


SCHEMA = make_executable_schema(_TYPE_DEF, query, user)

