import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, HttpUrl, Field

# Import related schemas AFTER they are defined or use forward references
# from .collection_part import CollectionPart
# from .collection_news import CollectionNews
# from .student_collection import StudentCollection
from app.models.collection import CollectionStatus  # Import Enum


# Shared properties
class CollectionBase(BaseModel):
    class_id: str  # Keep as string matching the model
    start: datetime
    end: datetime
    account_id: str
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    logo: Optional[HttpUrl] = None
    purpose: Optional[str] = None
    total_amount: Decimal = Field(..., max_digits=12, decimal_places=2)
    status: CollectionStatus


# Properties to receive on item creation
class CollectionCreate(CollectionBase):
    # created_by will be set from the token
    # creation_date is set by default
    pass


# Properties to receive on item update
class CollectionUpdate(BaseModel):
    # Allow updating only specific fields
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    account_id: Optional[str] = None
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    logo: Optional[HttpUrl] = None
    purpose: Optional[str] = None
    total_amount: Optional[Decimal] = Field(None, max_digits=12, decimal_places=2)
    status: Optional[CollectionStatus] = None


# Properties shared by models stored in DB
class CollectionInDBBase(CollectionBase):
    id: uuid.UUID
    creation_date: datetime
    created_by: str  # User ID from token

    class Config:
        orm_mode = True


# Properties to return to client (including relationships)
class Collection(CollectionInDBBase):
    # Example of including related items - adjust as needed
    # parts: List[CollectionPart] = []
    # news: List[CollectionNews] = []
    # student_collections: List[StudentCollection] = []
    pass


# Properties stored in DB
class CollectionInDB(CollectionInDBBase):
    pass
