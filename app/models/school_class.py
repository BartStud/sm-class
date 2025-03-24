import uuid
from sqlalchemy import Column, String, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base


class SchoolClass(Base):
    __tablename__ = "classes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    avatar = Column(String(255), nullable=True)
    start_year = Column(Date, nullable=False)
    number = Column(String(10), nullable=False)
    chat_id = Column(String(255), nullable=True)

    class_students = relationship(
        "ClassStudent", back_populates="school_class", cascade="all, delete-orphan"
    )
