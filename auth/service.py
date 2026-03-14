from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Response
import jwt
from pwdlib import PasswordHash
from sqlmodel import Session, select

from config import settings
from db.models import User


password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("dummypassword")  # To prevent timing attacks


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def get_user(session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def authenticate_user(session: Session, email: str, password: str) -> User | None:
    user = get_user(session, email)
    if not user:
        # Prevent timing attacks
        verify_password(password, DUMMY_HASH)
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> tuple[str, datetime]:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=settings.refresh_token_expire_days)
    )
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return token, expire


def access_token_max_age() -> int:
    return 60 * settings.access_token_expire_minutes


def refresh_token_max_age() -> int:
    return 60 * 60 * 24 * settings.refresh_token_expire_days


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # no JS access
        samesite="lax",  # your domain only
        secure=settings.cookie_secure,
        max_age=access_token_max_age(),
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,  # no JS access
        samesite="lax",  # your domain only
        secure=settings.cookie_secure,
        max_age=refresh_token_max_age(),
    )
