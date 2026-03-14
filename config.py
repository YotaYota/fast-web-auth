import os
import warnings
from typing import ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Settings are loaded from .env.{APP_ENV} (e.g. .env.local in dev).
# In production, APP_ENV=prod is set by the hosting platform and .env.prod
# does not exist — pydantic-settings silently ignores the missing file and
# reads variables directly from the environment instead.

env = os.getenv("APP_ENV", "local")  # default to local

if os.path.exists(".env.prod"):
    warnings.warn(
        ".env.prod file detected! Production secrets should be injected "
        "by the hosting platform, not stored in a file.",
        stacklevel=1,
    )


class Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=f".env.{env}",  # default to .env.local
        env_file_encoding="utf-8",
    )

    secret_key: str = Field(default=...)  # openssl rand -hex 32
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    cookie_secure: bool = True  # Set to True in production (HTTPS only)


settings = Settings()

assert len(settings.secret_key) >= 32, (
    "SECRET_KEY is too short! Generate one with: openssl rand -hex 32"
)
