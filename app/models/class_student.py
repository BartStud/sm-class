import uuid
from sqlalchemy import Column, ForeignKey, String, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base
from .enums import ClassStudentStatus


class ClassStudent(Base):
    __tablename__ = "class_students"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(String(255), nullable=False)
    class_id = Column(
        UUID(as_uuid=True), ForeignKey("classes.id", ondelete="CASCADE"), nullable=False
    )
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=True)
    status = Column(
        SQLAlchemyEnum(ClassStudentStatus, name="class_student_status_enum"),
        nullable=False,
        default=ClassStudentStatus.PENDING,
        index=True,
    )
    requested_by_parent_id = Column(String(255), nullable=True)

    school_class = relationship("SchoolClass", back_populates="class_students")
