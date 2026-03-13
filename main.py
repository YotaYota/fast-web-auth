from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.templating import Jinja2Templates

from auth.dependencies import get_current_active_user
from auth.models import User
from auth.router import router as auth_router


app = FastAPI()
app.include_router(auth_router)

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def landing(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request})

@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
    return current_user

@app.get("/protected")
async def protected_page(
    current_user: Annotated[User, Depends(get_current_active_user)]
    ) -> dict[str, str]:
    return {"message": f"Hello {current_user.username}!"}
