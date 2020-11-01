import logging
from typing import List, Optional
import datetime as dt
from starlette.requests import HTTPConnection  # type: ignore
from starlette.authentication import (  # type: ignore
    AuthenticationBackend,
    SimpleUser,
    AuthCredentials,
)
from passlib.context import CryptContext  # type: ignore
from jose import JWTError, jwt  # type: ignore
from app.config import AUTH_SECRET_KEY, AUTH_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


_log = logging.getLogger(__name__)
_crpt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenValidationFailed(Exception):
    pass


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
        raise TokenValidationFailed from err
    return TokenData(username=username, scopes=payload.get("scopes", []))


class AuthBackend(AuthenticationBackend):
    """
    Middleware backend for OAuth2 Acc. Token validation

    If Bearer token exists, validate it and add authenticated user to
    request.user. If not, add unauthenticated user (happens implicitly
    when returning None)
    """

    async def authenticate(self, conn: HTTPConnection):
        if "Authorization" not in conn.headers:
            return

        auth = conn.headers["Authorization"]

        try:
            scheme, credentials = auth.split()
            if scheme.lower() == "bearer":
                try:
                    data = validate_access_token(token=credentials)
                except TokenValidationFailed as err:
                    _log.info(
                        "Authorization header existed but token validation failed: %s",
                        err,
                    )
                    return
            else:
                _log.info("Authorization header existed but no Bearer was found")
                return
        except ValueError:
            _log.info("Authorization header existed but no scheme was found")
            return

        return AuthCredentials(scopes=data.scopes), SimpleUser(username=data.username)
