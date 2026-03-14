from datetime import timedelta

import jwt
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse

from auth.service import (
    create_access_token,
    create_refresh_token,
    get_user,
    set_auth_cookies,
)
from config import settings
from db.database import engine


class RefreshTokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Only intercept if access_token has expired (401) or redirect to login (307)
        if response.status_code not in (307, 401):
            return response

        # Read refresh_token from cookie
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            return response

        with Session(engine) as session:
            try:
                payload = jwt.decode(
                    refresh_token,
                    settings.secret_key,
                    algorithms=[settings.algorithm],
                )
                email: str | None = payload.get("sub")
                if not email:
                    return response

                # check refresh_token match DB
                user = get_user(session, email=email)
                if not user or user.refresh_token != refresh_token:
                    return response

                # Rotate refresh_token
                new_refresh_token, refresh_token_expires_at = create_refresh_token(
                    data={"sub": email},
                )
                user.refresh_token = new_refresh_token
                user.refresh_token_expires_at = refresh_token_expires_at
                session.add(user)
                session.commit()

            except InvalidTokenError:
                return response

        # Issue new access token
        new_access_token = create_access_token(
            data={"sub": email},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        )
        # Redirect to the same URL to retry with new access token
        redirect = RedirectResponse(url=str(request.url), status_code=307)
        set_auth_cookies(redirect, new_access_token, new_refresh_token)
        return redirect
