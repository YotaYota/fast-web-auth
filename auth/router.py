from datetime import timedelta, datetime, timezone
from typing import Annotated

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session

from auth.rate_limit import limiter
from auth.service import (
    authenticate_user,
    get_user,
    create_access_token,
    create_refresh_token,
    set_auth_cookies,
)
from templates import templates
from config import settings
from db.database import get_session


router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")


@router.post("/login")
@limiter.limit("5/minute")
async def login(
    request: Request,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    session: Annotated[Session, Depends(get_session)],
):
    user = authenticate_user(session, email, password)
    if not user:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Incorrect username or password"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    refresh_token, refresh_token_expires_at = create_refresh_token(
        data={"sub": user.email},
    )

    # Store refresh token in DB
    user.refresh_token = refresh_token
    user.refresh_token_expires_at = refresh_token_expires_at
    user.last_login = datetime.now(timezone.utc)
    session.add(user)
    session.commit()

    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    set_auth_cookies(response, access_token, refresh_token)
    return response


@router.get("/logout", response_class=HTMLResponse)
async def logout(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
):
    data = {"login_url": router.url_path_for("login_page")}
    response = templates.TemplateResponse(request, "logout.html", {"data": data})

    # Invalidate refresh_token in DB
    access_token = request.cookies.get("access_token")
    if access_token:
        try:
            payload = jwt.decode(
                access_token,
                settings.secret_key,
                algorithms=[settings.algorithm],
                options={"verify_exp": False},  # Ignore expiration for logout
            )
            email = payload.get("sub")
            if email:
                user = get_user(session, email)
                if user:
                    user.refresh_token = None
                    user.refresh_token_expires_at = None
                    session.add(user)
                    session.commit()
        except InvalidTokenError:
            pass  # Token is invalid, proceed with logout:

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response
