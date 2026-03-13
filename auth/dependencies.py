from typing import Annotated

import jwt
from fastapi import Cookie, Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError

from auth.models import TokenData, User
from auth.service import get_user
from config import settings

# Temporary until we have a real database
from db.fake import fake_users_db


# Extract a cookie named exactly "access_token" (by parameter name)
# On fail: redirect to /login (by header "Location")
# Note that 307 is used to preserves the original HTTP method. In case a
# POST happens on a protected route from a user who isn't logged in,
# a 302 would redirect them to /login as a GET — which is correct for /login
# but might not be for other protected routes.
def get_token_from_cookie(access_token: Annotated[str | None, Cookie()] = None) -> str:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login"},
        )
    return access_token


async def get_current_user(
    token: Annotated[str, Depends(get_token_from_cookie)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        # Validation also checks expiration time (exp claim)
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    if token_data.username is None:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
