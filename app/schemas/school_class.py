import uuid
from datetime import date
from typing import Optional
from pydantic import BaseModel, HttpUrl


# Shared properties
class SchoolClassBase(BaseModel):
    avatar: Optional[HttpUrl] = None
    start_year: date
    number: str
    chat_id: Optional[str] = None


# Properties to receive on item creation
class SchoolClassCreate(SchoolClassBase):
    pass


# Properties to receive on item update
class SchoolClassUpdate(SchoolClassBase):
    avatar: Optional[HttpUrl] = None
    start_year: Optional[date] = None
    number: Optional[str] = None
    chat_id: Optional[str] = None


# Properties shared by models stored in DB
class SchoolClassInDBBase(SchoolClassBase):
    id: uuid.UUID

    class Config:
        orm_mode = True  # Replaced from_attributes=True for Pydantic v1 compatibility if needed


# Properties to return to client
class SchoolClass(SchoolClassInDBBase):
    pass


# Properties stored in DB
class SchoolClassInDB(SchoolClassInDBBase):
    pass
