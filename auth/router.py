from datetime import timedelta, datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session

from auth.service import authenticate_user, create_access_token, create_refresh_token
from templates import templates
from config import settings
from db.database import get_session


router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    session: Annotated[Session, Depends(get_session)],
):
    user = authenticate_user(session, email, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Incorrect username or password"},
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
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # no JS access
        secure=settings.cookie_secure,  # HTTPS only when True
        samesite="lax",  # your domain only
        max_age=60 * 15,  # 15 minutes
    )
    return response


@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request, response: Response):
    data = {"login_url": router.url_path_for("login_page")}
    response = templates.TemplateResponse(
        "logout.html", {"request": request, "data": data}
    )
    response.delete_cookie("access_token")
    return response
