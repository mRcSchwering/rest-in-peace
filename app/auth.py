"""
Authentication and authorization related stuff

Im writing hashed passwords to the DB and comparing hashes.
As auth method I'm validating JWTs which can be provided to the
user via some login endpoint.
JWT carries a username and a scope.

I'm using a starlette authentication middleware.
Unfortunately starlette makes it hard to add custom objects
to the request, that's why I have to construct some
work-around classes.
"""
import logging
from typing import Union
import datetime as dt
from passlib.context import CryptContext  # type: ignore
from jose import JWTError, jwt  # type: ignore
from app.config import AUTH_SECRET_KEY, AUTH_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.exceptions import TokenValidationFailed
from app.db.base import get_db
import app.db.crud as crud
import app.db.models as models


_log = logging.getLogger(__name__)
_crpt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """get password hash"""
    return _crpt_context.hash(plain)


def password_matches(plain, hashed) -> bool:
    """True if pain and hashed password matches else False"""
    return _crpt_context.verify(plain, hashed)


def create_access_token(username: str) -> str:
    """Create JWT with username as sub"""
    scopes = ["user:authenticated"]
    expire = dt.datetime.utcnow() + dt.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        claims={"sub": username, "scopes": scopes, "exp": expire},
        key=AUTH_SECRET_KEY,
        algorithm=AUTH_ALGORITHM,
    )


def validate_access_token(token: str) -> str:
    """Validate access token and return username"""
    try:
        payload = jwt.decode(
            token=token, key=AUTH_SECRET_KEY, algorithms=[AUTH_ALGORITHM]
        )
        username: str = payload["sub"]
    except (JWTError, KeyError) as err:
        raise TokenValidationFailed(msg=f"Decoding failed: {err}") from err
    return username


class Auth:
    """
    Auth object to be passed over by the AuthBackend middleware.
    
    I need a separate object for this because if the AuthBackend
    returns `None` it will be converted to an (incompatible)
    `UnauthenticatedUser` object. Using this object basically as
    a container i.o. to also transport a `None`.

    Args:
        user: db user obj of an authenticated user
    """

    def _user_from_auth(self, auth: Union[str, None]) -> Union[None, models.User]:
        if auth is None:
            return None
        try:
            scheme, credentials = auth.split()
            if scheme.lower() == "bearer":
                try:
                    username = validate_access_token(token=credentials)
                except TokenValidationFailed:
                    return None
            else:
                _log.info("Authorization header existed but no Bearer was found")
                return None
        except ValueError:
            _log.info("Authorization header existed but no scheme was found")
            return None

        with get_db() as db:
            db_user = crud.get_user_by_email(db=db, email=username)
        return db_user

    def __init__(self, auth: str):
        user = self._user_from_auth(auth)
        self.is_authenticated = False if user is None else True
        self.user = user
