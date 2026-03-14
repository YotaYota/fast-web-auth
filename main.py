from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from auth.dependencies import get_current_active_user
from auth.models import UserPublic
from auth.rate_limit import limiter
from auth.router import router as auth_router
from templates import templates
from db.database import create_db_and_tables
from auth.middleware import RefreshTokenMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    create_db_and_tables()
    yield
    # shutdown (nothing to do yet)


app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(RefreshTokenMiddleware)
app.include_router(auth_router)


@app.get("/")
async def landing(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request})


@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
) -> UserPublic:
    return current_user


@app.get("/protected")
async def protected_page(
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
) -> dict[str, str]:
    return {"message": f"Hello {current_user.email}!"}
