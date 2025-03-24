import uuid
from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base


class CollectionNews(Base):
    __tablename__ = "collection_news"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collection_id = Column(
        UUID(as_uuid=True),
        ForeignKey("collections.id", ondelete="CASCADE"),
        nullable=False,
    )
    author_id = Column(String(255), nullable=False)
    date = Column(DateTime, nullable=False)
    content = Column(Text, nullable=False)

    collection = relationship("Collection", back_populates="news")
