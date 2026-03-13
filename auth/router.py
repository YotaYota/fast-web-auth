from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Form, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from auth.service import authenticate_user, create_access_token
from config import ACCESS_TOKEN_EXPIRE_MINUTES
from db.fake import fake_users_db

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    user = authenticate_user(fake_users_db, username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": {}, "error": "Incorrect username or password"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    response = RedirectResponse(
        url="/",
        status_code=status.HTTP_303_SEE_OTHER
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,             # 🔒 no JS access
        secure=True,               # 🔒 HTTPS only
        samesite="lax",            # 🔒 your domain only
        max_age=60 * 60 * 24 * 7,  # ⏱️ 7 days
    )
    return response

@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request, response: Response):
    data = {"login_url": router.url_path_for("login_page")}
    response = templates.TemplateResponse("logout.html", {"request": request, "data": data})
    response.delete_cookie("access_token")
    return response
