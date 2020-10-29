"""
Testing configuration and helpers

Imports models and session factory from app.db to initialize a database session
and provide a `reset_testdata()` function, also as __main__ (`python -m test.conftest`).
Assumes that app is running on `http://localhost:8000`.
Overwrite with environment var `HOST`.
"""
import os
import datetime as dt
import requests
from sqlalchemy.orm.session import close_all_sessions  # type: ignore
from app.db.base import SessionLocal, engine
import app.db.models as models

host = os.environ.get("HOST", "http://localhost:8000")
db = SessionLocal()


def query(querystr: str) -> requests.Response:
    """Query GraphQL API, paste query string from GraphiQL"""
    return requests.post(host + "/", json={"query": querystr}, timeout=1)


def reset_testdata():
    print("resetting testdata")
    close_all_sessions()
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)

    db.add_all(
        [
            models.User(
                name="Active Harry",
                email="active.harry@gmail.com",
                hashed_password="asdf1",
                is_active=True,
                is_superuser=False,
            ),
            models.User(
                name="Inactive Joe",
                email="inactive.joe@gmail.com",
                hashed_password="asdf2",
                is_active=False,
                is_superuser=False,
            ),
            models.User(
                name="Super Susi",
                email="super.susi@gmail.com",
                hashed_password="asdf3",
                is_active=True,
                is_superuser=True,
            ),
        ]
    )

    db.add_all(
        [
            models.Item(
                title="Harry's shampoo",
                description="Smells good",
                owner_dbid=1,
                posted_on=dt.date(2000, 1, 1),
            ),
            models.Item(
                title="Harry's hairbrush",
                description="For hairy situations",
                owner_dbid=1,
                posted_on=dt.date(2000, 12, 11),
            ),
            models.Item(
                title="Joe's pen",
                description="Long forgotten",
                owner_dbid=2,
                posted_on=dt.date(2001, 7, 1),
            ),
            models.Item(
                title="Susi's apple",
                description="Shouldn't eat anymore",
                owner_dbid=3,
                posted_on=dt.date(2001, 9, 1),
            ),
        ]
    )

    db.commit()
    db.close()


# TODO: There is an issue with changing the DB while the app
#       is running. I think graphene keeps connections open.
#       see: https://github.com/graphql-python/graphene-sqlalchemy/issues/292
# @pytest.fixture(scope="module")
# def reset():
#     """
#     Module scoped fixtures will be started once for every
#     module, then run all tests in that module, then have
#     the exit run once.
#     """
#     reset_testdata()
#     yield
#     reset_testdata()


if __name__ == "__main__":
    reset_testdata()
