from pydantic import BaseModel

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    email: str
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str
