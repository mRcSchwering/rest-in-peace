"""
Mutation resolvers
"""
from contextlib import contextmanager
from ariadne import MutationType, ObjectType  # type: ignore
from ariadne.types import GraphQLResolveInfo  # type: ignore
from app.db.base import get_db
from app.auth import Auth
import app.db.crud as crud
import app.db.models as models
from app.auth import password_matches, create_access_token, hash_password

mutation = MutationType()
me_type = ObjectType("Me")
item_type = ObjectType("Item")


@contextmanager
def admin_auth(info: GraphQLResolveInfo):
    with get_db() as db:
        auth = Auth.from_info(info=info, db=db)
        if auth.user is None or not auth.user.isAdmin:
            raise ValueError("Not logged in as admin")
        yield db


@mutation.field("login")
def resolve_login(*_, **kwargs):
    email = kwargs["input"]["email"]
    password = kwargs["input"]["password"]
    with get_db() as db:
        db_user = crud.get_user_by_email(db=db, email=email)

    if db_user is None or not password_matches(
        plain=password, hashed=db_user.hashedPassword
    ):
        raise ValueError("Email or password wrong")

    return {"token": create_access_token(username=db_user.email), "me": db_user}


@mutation.field("createMe")
def resolve_create_me(*_, **kwargs):
    email = kwargs["input"]["email"]
    password = kwargs["input"]["password"]

    if len(email) < 4:
        raise ValueError("Email must be at least 4 characters long")

    if len(password) < 4:
        raise ValueError("Password must be at least 4 characters long")

    with get_db() as db:
        db_user = crud.create_user(
            db=db, hashedPassword=hash_password(password), **kwargs["input"]
        )
    return {"token": create_access_token(username=db_user.email), "me": db_user}


@mutation.field("updateMe")
def resolve_update_me(_, info: GraphQLResolveInfo, **kwargs):
    inputs = kwargs.get("input", {})
    with get_db() as db:
        auth = Auth.from_info(info=info, db=db)
        if auth.user is None:
            raise ValueError("Not logged in")
        return crud.update_user(
            db=db,
            user=auth.user,
            name=inputs.get("name", crud.Undefined),
            isActive=inputs.get("isActive", crud.Undefined),
        )


@me_type.field("items")
def resolve_my_items(parent: models.User, unused, **_):
    del unused
    with get_db() as db:
        return crud.get_items_by_owner_id(db=db, ownerId=parent.id)


@mutation.field("createItem")
def resolve_create_item(_, info: GraphQLResolveInfo, **kwargs):
    with get_db() as db:
        auth = Auth.from_info(info=info, db=db)
        if auth.user is None:
            raise ValueError("Not logged in")
        return crud.create_item(db=db, ownerId=auth.user.id, **kwargs["input"])


@mutation.field("updateItem")
def resolve_update_item(_, info: GraphQLResolveInfo, **kwargs):
    inputs = kwargs.get("input", {})
    with get_db() as db:
        auth = Auth.from_info(info=info, db=db)
        if auth.user is None:
            raise ValueError("Not logged in")
        return crud.update_item(
            db=db,
            ownerId=auth.user.id,
            itemId=kwargs["id"],
            title=inputs.get("title", crud.Undefined),
            description=inputs.get("description", crud.Undefined),
            postedOn=inputs.get("postedOn", crud.Undefined),
        )


@item_type.field("owner")
def resolve_item_owner(parent: models.Item, unused, **_):
    del unused
    with get_db() as db:
        return crud.get_user_by_id(db=db, id=parent.ownerId)


@mutation.field("deleteUser")
def delete_user(_, info: GraphQLResolveInfo, **kwargs):
    with admin_auth(info) as db:
        return crud.delete_user(db=db, id=int(kwargs["id"]))


@mutation.field("deleteItem")
def delete_item(_, info: GraphQLResolveInfo, **kwargs):
    with admin_auth(info) as db:
        return crud.delete_item(db=db, id=int(kwargs["id"]))


mutations = (mutation, me_type, item_type)

