import enum


class ClassStudentStatus(enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    REJECTED = "rejected"
    ENDED = "ended"
