from typing import Annotated

import jwt
from fastapi import Cookie, Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session

from auth.models import UserPublic
from auth.service import get_user
from config import settings
from db.database import get_session


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
    session: Annotated[Session, Depends(get_session)],
) -> UserPublic:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        # Validation also checks expiration time (exp claim)
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = get_user(session, email=email)
    if user is None:
        raise credentials_exception
    return UserPublic.model_validate(user)


async def get_current_active_user(
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> UserPublic:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
