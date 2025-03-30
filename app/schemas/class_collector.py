import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# Shared properties
class ClassCollectorBase(BaseModel):
    parent_id: str
    class_id: uuid.UUID
    start: datetime
    end: Optional[datetime] = None


# Properties to receive on item creation
class ClassCollectorCreate(BaseModel):
    # Usually created via class endpoint, maybe just need parent_id and start/end?
    parent_id: str
    start: datetime = datetime.now()  # Default start time
    end: Optional[datetime] = None


# Properties to receive on item update (e.g., setting end date)
class ClassCollectorUpdate(BaseModel):
    end: Optional[datetime] = None


# Properties shared by models stored in DB
class ClassCollectorInDBBase(ClassCollectorBase):
    id: uuid.UUID

    class Config:
        orm_mode = True


# Properties to return to client
class ClassCollector(ClassCollectorInDBBase):
    pass


# Properties stored in DB
class ClassCollectorInDB(ClassCollectorInDBBase):
    pass
