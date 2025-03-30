import uuid
from typing import List, Optional
from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.class_student import ClassStudent
from app.models.enums import ClassStudentStatus
from app.schemas.class_student import ClassStudentRequestCreate, ClassStudentUpdate


class CRUDClassStudent:
    async def get(self, db: AsyncSession, id: uuid.UUID) -> Optional[ClassStudent]:
        result = await db.execute(select(ClassStudent).filter(ClassStudent.id == id))
        return result.scalars().first()

    async def get_by_student_and_class(
        self, db: AsyncSession, *, student_id: str, class_id: uuid.UUID
    ) -> Optional[ClassStudent]:
        """Pobiera przypisanie studenta do konkretnej klasy."""
        result = await db.execute(
            select(ClassStudent).filter_by(student_id=student_id, class_id=class_id)
        )
        return (
            result.scalars().first()
        )  # Może być więcej niż jeden historycznie? Rozważ filtrowanie po statusie/dacie

    async def get_multi_by_class(
        self,
        db: AsyncSession,
        *,
        class_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ClassStudentStatus] = None,  # Dodaj filtr statusu
    ) -> List[ClassStudent]:
        statement = select(ClassStudent).filter(ClassStudent.class_id == class_id)
        if status:
            statement = statement.filter(ClassStudent.status == status)

        # Sortowanie, np. po dacie dodania lub statusie
        statement = (
            statement.order_by(ClassStudent.start.desc()).offset(skip).limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()

    async def get_multi_by_student(
        self,
        db: AsyncSession,
        *,
        student_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ClassStudentStatus] = None,  # Dodaj filtr statusu
    ) -> List[ClassStudent]:
        """Pobiera wszystkie przypisania danego studenta do klas."""
        statement = select(ClassStudent).filter(ClassStudent.student_id == student_id)
        if status:
            statement = statement.filter(ClassStudent.status == status)
        statement = (
            statement.order_by(ClassStudent.start.desc()).offset(skip).limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()

    async def create_request(
        self,
        db: AsyncSession,
        *,
        obj_in: ClassStudentRequestCreate,
        class_id: uuid.UUID,
        requested_by_parent_id: str,
    ) -> ClassStudent:
        """Tworzy zgłoszenie dodania studenta do klasy przez rodzica."""
        # Sprawdź, czy już nie istnieje aktywne lub oczekujące zgłoszenie dla tej pary
        existing = await db.execute(
            select(ClassStudent).filter(
                and_(
                    ClassStudent.student_id == obj_in.student_id,
                    ClassStudent.class_id == class_id,
                    ClassStudent.status.in_(
                        [ClassStudentStatus.ACTIVE, ClassStudentStatus.PENDING]
                    ),
                )
            )
        )
        if existing.scalars().first():
            raise ValueError(
                f"Student {obj_in.student_id} already has an active or pending request for class {class_id}"
            )

        db_obj = ClassStudent(
            student_id=obj_in.student_id,
            class_id=class_id,
            start=datetime.now(),  # Data zgłoszenia
            status=ClassStudentStatus.PENDING,  # Zawsze jako oczekujące
            requested_by_parent_id=requested_by_parent_id,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_status(
        self, db: AsyncSession, *, db_obj: ClassStudent, new_status: ClassStudentStatus
    ) -> ClassStudent:
        """Aktualizuje status przypisania (np. akceptacja/odrzucenie)."""
        if (
            new_status == ClassStudentStatus.ACTIVE
            and db_obj.status != ClassStudentStatus.PENDING
        ):
            # Można aktywować tylko oczekujące zgłoszenie (lub np. zakończone?)
            raise ValueError(f"Cannot activate assignment with status {db_obj.status}")
        if new_status == ClassStudentStatus.ACTIVE:
            # Ustaw datę startową na teraz, jeśli aktywujemy? Lub zostaw datę zgłoszenia?
            # db_obj.start = datetime.now() # Rozważ, czy to potrzebne
            pass  # Na razie zostawiamy datę zgłoszenia jako start
        elif new_status == ClassStudentStatus.ENDED:
            db_obj.end = datetime.now()  # Ustaw datę zakończenia

        db_obj.status = new_status
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    # Funkcja 'update' może pozostać do ogólnych zmian, ale zmiana statusu przez dedykowaną funkcję
    async def update(
        self, db: AsyncSession, *, db_obj: ClassStudent, obj_in: ClassStudentUpdate
    ) -> ClassStudent:
        update_data = obj_in.dict(exclude_unset=True)
        # Nie pozwól na zmianę statusu przez tę ogólną funkcję, użyj update_status
        if "status" in update_data:
            del update_data["status"]  # Lub rzuć błąd
        if "end" in update_data:
            db_obj.end = update_data["end"]
            # Jeśli ustawiono datę zakończenia, zmień status na ENDED?
            if update_data["end"] and update_data["end"] <= datetime.now():
                db_obj.status = ClassStudentStatus.ENDED

        # Tutaj można dodać logikę dla innych pól, jeśli są
        # for field, value in update_data.items():
        #     setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(
        self, db: AsyncSession, *, id: uuid.UUID
    ) -> Optional[ClassStudent]:
        db_obj = await self.get(db=db, id=id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
        return db_obj


class_student = CRUDClassStudent()
