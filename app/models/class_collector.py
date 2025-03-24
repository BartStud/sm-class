import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base


class ClassCollector(Base):
    __tablename__ = "class_collectors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id = Column(String(255), nullable=False)
    class_id = Column(
        UUID(as_uuid=True), ForeignKey("classes.id", ondelete="CASCADE"), nullable=False
    )
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=True)

    class_ = relationship("Class", back_populates="class_collectors")
