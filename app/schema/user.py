from pydantic import BaseModel


class UserResponse(BaseModel):
    id: str
    avatar: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    username: str | None = None
    email: str | None = None
    role: str | None = None


class UserUpdate(BaseModel):
    avatar: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    username: str | None = None
    email: str | None = None
