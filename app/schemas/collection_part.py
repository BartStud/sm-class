import uuid
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Optional
from app.models.collection_part import PaymentType  # Import Enum


# Shared properties
class CollectionPartBase(BaseModel):
    name: str = Field(..., max_length=255)
    collection_id: uuid.UUID  # Usually set via path param, not body
    total_amount: Decimal = Field(..., max_digits=12, decimal_places=2)
    payment_type: PaymentType


# Properties to receive on item creation
class CollectionPartCreate(BaseModel):
    # collection_id will come from the path parameter typically
    name: str = Field(..., max_length=255)
    total_amount: Decimal = Field(..., max_digits=12, decimal_places=2)
    payment_type: PaymentType


# Properties to receive on item update
class CollectionPartUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    total_amount: Optional[Decimal] = Field(None, max_digits=12, decimal_places=2)
    payment_type: Optional[PaymentType] = None


# Properties shared by models stored in DB
class CollectionPartInDBBase(CollectionPartBase):
    id: uuid.UUID

    class Config:
        orm_mode = True


# Properties to return to client
class CollectionPart(CollectionPartInDBBase):
    pass


# Properties stored in DB
class CollectionPartInDB(CollectionPartInDBBase):
    pass
