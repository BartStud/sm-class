from datetime import date
from pydantic import BaseModel


class ChildBase(BaseModel):
    avatar: str | None = None
    firstName: str
    lastName: str
    birthDate: date

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        # mapowanie z bazy (snake_case) do camelCase w odpowiedzi
        fields = {
            "firstName": "first_name",
            "lastName": "last_name",
            "birthDate": "birth_date",
        }


class ChildCreate(ChildBase):
    pass


class ChildUpdate(BaseModel):
    avatar: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    birthDate: date | None = None

    class Config:
        allow_population_by_field_name = True
        fields = {
            "firstName": "first_name",
            "lastName": "last_name",
            "birthDate": "birth_date",
        }


class ChildOut(ChildBase):
    id: str


class ParentOut(BaseModel):
    id: str
    avatar: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    username: str | None = None
    email: str | None = None

    class Config:
        orm_mode = True


class ChildDetailResponse(ChildOut):
    parent: ParentOut
