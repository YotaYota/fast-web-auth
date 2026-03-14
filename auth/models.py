from pydantic import BaseModel, ConfigDict


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: str
    name: str | None = None
    is_admin: bool = False
    disabled: bool = False
