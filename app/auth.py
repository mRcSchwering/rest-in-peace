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
from typing import List, Optional
import datetime as dt
from starlette.requests import HTTPConnection  # type: ignore
from starlette.authentication import AuthenticationBackend, AuthCredentials  # type: ignore
from passlib.context import CryptContext  # type: ignore
from jose import JWTError, jwt  # type: ignore
from app.config import AUTH_SECRET_KEY, AUTH_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.exceptions import TokenValidationFailed
from app.db.base import get_db
import app.db.crud as crud
import app.db.models as models


_log = logging.getLogger(__name__)
_crpt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData:
    """Container for username and scopes"""

    _default_scopes = ["authenticated"]

    def __init__(self, username: str, scopes: Optional[List[str]] = None):
        self.username = username
        self.scopes = self._default_scopes if scopes is None else scopes


def hash_password(plain: str) -> str:
    """get password hash"""
    return _crpt_context.hash(plain)


def password_matches(plain, hashed) -> bool:
    """True if pain and hashed password matches else False"""
    return _crpt_context.verify(plain, hashed)


def create_access_token(token_data: TokenData) -> str:
    """Create JWT with username as sub"""
    expire = dt.datetime.utcnow() + dt.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        claims={"sub": token_data.username, "scopes": token_data.scopes, "exp": expire},
        key=AUTH_SECRET_KEY,
        algorithm=AUTH_ALGORITHM,
    )


def validate_access_token(token: str) -> TokenData:
    """Validate access token and return TokenData"""
    try:
        payload = jwt.decode(
            token=token, key=AUTH_SECRET_KEY, algorithms=[AUTH_ALGORITHM]
        )
        username: str = payload["sub"]
    except (JWTError, KeyError) as err:
        raise TokenValidationFailed(msg=f"Decoding failed: {err}") from err
    return TokenData(username=username, scopes=payload.get("scopes", []))


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

    def __init__(self, user: Optional[models.User] = None):
        self.is_authenticated = False if user is None else True
        self.user = user


class AuthBackend(AuthenticationBackend):
    """
    Middleware backend for JWT validation

    If Bearer token exists, validate it and add authenticated user to
    request.user. If not, have a `None` user (wrapped in `Auth`).

    Will be accessible in resolver's GraphQLResolveInfo:
        auth: Auth = info.context["request"].user
        auth.is_authenticated
        auth.user
    """

    async def authenticate(self, conn: HTTPConnection):
        if "Authorization" not in conn.headers:
            return None, Auth()

        auth = conn.headers["Authorization"]

        try:
            scheme, credentials = auth.split()
            if scheme.lower() == "bearer":
                try:
                    data = validate_access_token(token=credentials)
                except TokenValidationFailed:
                    return [], Auth()
            else:
                _log.info("Authorization header existed but no Bearer was found")
                return [], Auth()
        except ValueError:
            _log.info("Authorization header existed but no scheme was found")
            return [], Auth()

        with get_db() as db:
            db_user = crud.get_user_by_email(db=db, email=data.username)
        return AuthCredentials(scopes=data.scopes), Auth(db_user)
