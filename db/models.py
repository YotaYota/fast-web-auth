from datetime import datetime, timezone
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    name: str | None = None
    disabled: bool = False
    is_admin: bool = False
    refresh_token: str | None = None
    refresh_token_expires_at: datetime | None = None
    last_login: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
