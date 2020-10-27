## App

This is a _fastAPI_ GraphQL app with _graphene_.
Generally I'm using a setup as described [here](https://fastapi.tiangolo.com/advanced/graphql/).
There is an extension for using _SQLAlchemy_ with _graphene_ -- [graphene_sqlalchemy](https://docs.graphene-python.org/projects/sqlalchemy/en/latest/).
I basically implemented [this example](https://docs.graphene-python.org/projects/sqlalchemy/en/latest/examples/#search-all-models-with-union)
from it for automatically generating queries from _SQLAlchemy_ model definitions.
Mutations still have to be done by hand.
