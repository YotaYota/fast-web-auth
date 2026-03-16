import jwt

from auth.service import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from config import settings


def test_password_hash_roundtrip():
    password = "mysecretpassword"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_create_access_token_contains_sub():
    token = create_access_token(data={"sub": "user@example.com"})
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    assert payload["sub"] == "user@example.com"
    assert "exp" in payload


def test_create_refresh_token_returns_expiry():
    token, expires_at = create_refresh_token(data={"sub": "user@example.com"})
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    assert payload["sub"] == "user@example.com"
    assert expires_at is not None


def test_authenticate_user_success(session, test_user):
    user = authenticate_user(session, "test@example.com", "testpassword123")
    assert user is not None
    assert user.email == "test@example.com"


def test_authenticate_user_wrong_password(session, test_user):
    assert authenticate_user(session, "test@example.com", "wrongpassword") is None


def test_authenticate_user_nonexistent(session):
    assert authenticate_user(session, "nobody@example.com", "whatever") is None
