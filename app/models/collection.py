import uuid
import enum
from datetime import datetime
from sqlalchemy import (
    Column,
    Enum,
    String,
    DateTime,
    Numeric,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base


class CollectionStatus(enum.Enum):
    NEW = "new"
    ACTIVE = "Active"
    BLOCKED = "Blocked"
    CANCELLED = "Cancelled"
    CLOSED = "Closed"


class Collection(Base):
    __tablename__ = "collections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    class_id = Column(String(255), nullable=False)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    creation_date = Column(DateTime, default=datetime.now)
    created_by = Column(String(255), nullable=False)
    account_id = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    logo = Column(String(255), nullable=True)
    purpose = Column(Text)
    total_amount = Column(Numeric(12, 2), nullable=False)
    status = Column(
        Enum(CollectionStatus, name="collection_status_enum"), nullable=False
    )

    parts = relationship(
        "CollectionPart", back_populates="collection", cascade="all, delete-orphan"
    )
    news = relationship(
        "CollectionNews", back_populates="collection", cascade="all, delete-orphan"
    )
    student_collections = relationship(
        "StudentCollection", back_populates="collection", cascade="all, delete-orphan"
    )
