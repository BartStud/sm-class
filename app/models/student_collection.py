from sqlalchemy import Column, String, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base


class StudentCollection(Base):
    __tablename__ = "student_collections"

    student_id = Column(String(255), primary_key=True)
    collection_id = Column(
        UUID(as_uuid=True),
        ForeignKey("collections.id", ondelete="CASCADE"),
        primary_key=True,
    )
    total_amount = Column(Numeric(12, 2), nullable=False)

    collection = relationship("Collection", back_populates="student_collections")
