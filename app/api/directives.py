"""Schema directives"""
from typing import Dict, Type
from ariadne.types import GraphQLResolveInfo  # type: ignore
from ariadne import SchemaDirectiveVisitor  # type: ignore
from graphql import default_field_resolver
from app.auth import Auth


class Superuser(SchemaDirectiveVisitor):
    """Show a field only if user is superuser"""

    def visit_field_definition(self, field, object_type):
        original_resolver = field.resolve or default_field_resolver

        def resolve_field(obj, info: GraphQLResolveInfo, **kwargs):
            result = original_resolver(obj, info, **kwargs)
            auth: Auth = info.context["auth"]
            if auth.user is not None and auth.user.is_superuser:
                return result
            return None

        field.resolve = resolve_field
        return field


directives: Dict[str, Type[SchemaDirectiveVisitor]] = {"superuser": Superuser}

