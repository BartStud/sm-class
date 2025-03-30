import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


# Shared properties
class CollectionNewsBase(BaseModel):
    collection_id: uuid.UUID  # Usually set via path param
    content: str


# Properties to receive on item creation
class CollectionNewsCreate(BaseModel):
    # collection_id will come from path
    # author_id will come from token
    # date will be set now
    content: str


# Properties to receive on item update (Maybe only content is updatable?)
class CollectionNewsUpdate(BaseModel):
    content: Optional[str] = None


# Properties shared by models stored in DB
class CollectionNewsInDBBase(CollectionNewsBase):
    id: uuid.UUID
    author_id: str  # User ID from token
    date: datetime

    class Config:
        orm_mode = True


# Properties to return to client
class CollectionNews(CollectionNewsInDBBase):
    pass


# Properties stored in DB
class CollectionNewsInDB(CollectionNewsInDBBase):
    pass
