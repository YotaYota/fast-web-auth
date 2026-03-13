from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from auth.models import UserInDB
from config import settings


password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("dummypassword")  # To prevent timing attacks


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def get_user(db: dict, username: str) -> UserInDB | None:
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None


def authenticate_user(fake_db: dict, username: str, password: str) -> UserInDB | None:
    user = get_user(fake_db, username)
    if not user:
        verify_password(password, DUMMY_HASH)  # To prevent timing attacks
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt
