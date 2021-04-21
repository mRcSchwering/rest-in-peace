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
from app.db.base import SessionFact, engine
import app.db.models as models

host = os.environ.get("HOST", "http://localhost:8000")
db = SessionFact()


def query(querystr: str, jwt: str = None) -> requests.Response:
    """Query GraphQL API, paste query string from GraphiQL"""
    if jwt is not None:
        headers = {"Authorization": f"Bearer {jwt}"}
    else:
        headers = {}
    return requests.post(
        host + "/", json={"query": querystr}, headers=headers, timeout=1
    )


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
                hashedPassword="$2b$12$.We4evbzf63bYRNaBlPnYuC/uu6SY5zgDCJGx7DtRyPkiRBrQ751u",  # asdf1
                isActive=True,
                isSuperuser=False,
            ),
            models.User(
                name="Inactive Joe",
                email="inactive.joe@gmail.com",
                hashedPassword="$2b$12$Od2WGjAOV1ByeQUEz05NIepeR4XQPjanVzM2Cl4.KMLb/C60Nzf7O",  # asdf2
                isActive=False,
                isSuperuser=False,
            ),
            models.User(
                name="Super Susi",
                email="super.susi@gmail.com",
                hashedPassword="$2b$12$gV0ulQXEARykTw4I7QTTYOyH4gYR12WoO/fN8BeZzsc5x9Jlyh4va",  # asdf3
                isActive=True,
                isSuperuser=True,
            ),
        ]
    )

    db.add_all(
        [
            models.Item(
                title="Harry's shampoo",
                description="Smells good",
                ownerId=1,
                postedOn=dt.date(2000, 1, 1),
            ),
            models.Item(
                title="Harry's hairbrush",
                description="For hairy situations",
                ownerId=1,
                postedOn=dt.date(2000, 12, 11),
            ),
            models.Item(
                title="Joe's pen",
                description="Long forgotten",
                ownerId=2,
                postedOn=dt.date(2001, 7, 1),
            ),
            models.Item(
                title="Susi's apple",
                description="Shouldn't eat anymore",
                ownerId=3,
                postedOn=dt.date(2001, 9, 1),
            ),
        ]
    )

    db.commit()
    db.close()


if __name__ == "__main__":
    reset_testdata()
