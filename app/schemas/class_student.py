import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.enums import ClassStudentStatus


# Shared properties
class ClassStudentBase(BaseModel):
    student_id: str
    class_id: uuid.UUID
    start: datetime
    end: Optional[datetime] = None
    status: ClassStudentStatus
    requested_by_parent_id: Optional[str] = None


# Properties to receive when a parent requests to add a child
class ClassStudentRequestCreate(BaseModel):
    student_id: str  # Rodzic podaje ID swojego dziecka


# Schema for creating directly (e.g., by admin, maybe not used by parent/collector flow)
class ClassStudentCreateInternal(BaseModel):
    student_id: str
    class_id: uuid.UUID  # Potrzebne jeśli tworzymy bezpośrednio
    start: datetime = Field(default_factory=datetime.now)
    end: Optional[datetime] = None
    status: ClassStudentStatus = ClassStudentStatus.PENDING  # Domyślnie
    requested_by_parent_id: Optional[str] = None


# Properties to receive on item update (e.g., setting end date or status)
class ClassStudentUpdate(BaseModel):
    end: Optional[datetime] = None
    status: Optional[ClassStudentStatus] = None  # Pozwól na zmianę statusu


# Properties shared by models stored in DB
class ClassStudentInDBBase(ClassStudentBase):
    id: uuid.UUID

    class Config:
        orm_mode = True


# Properties to return to client
class ClassStudent(ClassStudentInDBBase):
    pass


# Properties stored in DB
class ClassStudentInDB(ClassStudentInDBBase):
    pass


# Nowy endpoint do akceptacji/odrzucenia
class ClassStudentStatusUpdate(BaseModel):
    status: ClassStudentStatus  # Oczekuje tylko nowego statusu
