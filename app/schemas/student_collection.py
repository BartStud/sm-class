import uuid
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field


# Shared properties
class StudentCollectionBase(BaseModel):
    student_id: str
    collection_id: uuid.UUID
    total_amount: Decimal = Field(..., max_digits=12, decimal_places=2)


# Properties to receive on item creation/update
# Often managed via collection/class endpoints rather than directly
class StudentCollectionCreate(BaseModel):
    # collection_id from path
    student_id: str
    total_amount: Decimal = Field(..., max_digits=12, decimal_places=2)


class StudentCollectionUpdate(BaseModel):
    # Only amount seems updatable
    total_amount: Optional[Decimal] = Field(None, max_digits=12, decimal_places=2)


# Properties shared by models stored in DB
class StudentCollectionInDBBase(StudentCollectionBase):
    # Note: Composite primary key (student_id, collection_id)
    # Pydantic doesn't directly model composite keys, treat them as regular fields

    class Config:
        orm_mode = True


# Properties to return to client
class StudentCollection(StudentCollectionInDBBase):
    pass


# Properties stored in DB
class StudentCollectionInDB(StudentCollectionInDBBase):
    pass
