from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # openssl rand -hex 32
    secret_key: str = "5dd34369187bb8e728d00563e2de0458da504738f0148df5de6483cf89f1a8c1"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    cookie_secure: bool = True  # Set to True in production (HTTPS only)


settings = Settings()
