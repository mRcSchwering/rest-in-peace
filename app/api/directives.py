"""GraphQL schema directives"""
from typing import Dict, Type
from ariadne.types import GraphQLResolveInfo  # type: ignore
from ariadne import SchemaDirectiveVisitor  # type: ignore
from graphql import default_field_resolver
from app.db.base import get_db
from app.auth import Auth


class Superuser(SchemaDirectiveVisitor):
    """Show a field only if user is superuser"""

    def visit_field_definition(self, field, object_type):
        original_resolver = field.resolve or default_field_resolver

        def resolve_field(obj, info: GraphQLResolveInfo, **kwargs):
            result = original_resolver(obj, info, **kwargs)

            with get_db() as db:
                auth = Auth.from_info(info=info, db=db)
                if auth.user is None or not auth.user.isSuperuser:
                    return None
                return result

        field.resolve = resolve_field
        return field


directives: Dict[str, Type[SchemaDirectiveVisitor]] = {"superuser": Superuser}

