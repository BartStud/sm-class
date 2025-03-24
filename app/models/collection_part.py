import uuid
import enum
from sqlalchemy import Column, String, Numeric, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base


class PaymentType(enum.Enum):
    TOTAL_FIXED = "totalFixed"
    PERSON_FIXED = "personFixed"


class CollectionPart(Base):
    __tablename__ = "collection_parts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    collection_id = Column(
        UUID(as_uuid=True),
        ForeignKey("collections.id", ondelete="CASCADE"),
        nullable=False,
    )
    total_amount = Column(Numeric(12, 2), nullable=False)
    payment_type = Column(Enum(PaymentType, name="payment_type_enum"), nullable=False)

    collection = relationship("Collection", back_populates="parts")
