import uuid
from typing import List, Optional, Tuple

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student_collection import StudentCollection
from app.schemas.student_collection import (
    StudentCollectionCreate,
    StudentCollectionUpdate,
)


class CRUDStudentCollection:
    async def get(
        self, db: AsyncSession, *, student_id: str, collection_id: uuid.UUID
    ) -> Optional[StudentCollection]:
        result = await db.execute(
            select(StudentCollection).filter_by(
                student_id=student_id, collection_id=collection_id
            )
        )
        return result.scalars().first()

    async def get_multi_by_collection(
        self,
        db: AsyncSession,
        *,
        collection_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[StudentCollection]:
        result = await db.execute(
            select(StudentCollection)
            .filter(StudentCollection.collection_id == collection_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_multi_by_student(
        self, db: AsyncSession, *, student_id: str, skip: int = 0, limit: int = 100
    ) -> List[StudentCollection]:
        result = await db.execute(
            select(StudentCollection)
            .filter(StudentCollection.student_id == student_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: StudentCollectionCreate,
        collection_id: uuid.UUID
    ) -> StudentCollection:
        """Tworzy wpis uczestnictwa studenta w zbiórce."""
        # Sprawdź, czy już nie istnieje (opcjonalne, zależy od logiki - upsert vs create)
        # existing = await self.get(db=db, student_id=obj_in.student_id, collection_id=collection_id)
        # if existing:
        #     raise ValueError("Student already participating in this collection") # Lub inna obsługa błędu

        db_obj = StudentCollection(
            student_id=obj_in.student_id,
            collection_id=collection_id,
            total_amount=obj_in.total_amount,
        )
        db.add(db_obj)
        await db.commit()
        # Nie ma auto-generowanego ID, więc refresh nie jest konieczny dla kluczy
        # await db.refresh(db_obj) # Nie zadziała bez primary key ID
        return db_obj  # Zwraca obiekt z danymi wejściowymi

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: StudentCollection,
        obj_in: StudentCollectionUpdate
    ) -> StudentCollection:
        """Aktualizuje dane uczestnictwa studenta (głównie kwotę)."""
        update_data = obj_in.dict(exclude_unset=True)
        if "total_amount" in update_data:
            db_obj.total_amount = update_data["total_amount"]

        db.add(
            db_obj
        )  # Mimo że obiekt jest już śledzony, dodanie go oznacza, że ma być utrwalony
        await db.commit()
        # await db.refresh(db_obj) # Nie zadziała bez primary key ID
        return db_obj

    async def remove(
        self, db: AsyncSession, *, student_id: str, collection_id: uuid.UUID
    ) -> Optional[StudentCollection]:
        """Usuwa wpis uczestnictwa studenta w zbiórce."""
        db_obj = await self.get(
            db=db, student_id=student_id, collection_id=collection_id
        )
        if db_obj:
            # SQLAlchemy < 2.0 może wymagać innego podejścia do delete na composite key
            # W nowszych wersjach:
            await db.delete(db_obj)
            await db.commit()
            return db_obj  # Zwraca obiekt, który został usunięty
        return None

    # Opcjonalna metoda Upsert (Create or Update)
    async def upsert(
        self,
        db: AsyncSession,
        *,
        obj_in: StudentCollectionCreate,
        collection_id: uuid.UUID
    ) -> StudentCollection:
        db_obj = await self.get(
            db=db, student_id=obj_in.student_id, collection_id=collection_id
        )
        if db_obj:
            # Update existing
            update_schema = StudentCollectionUpdate(total_amount=obj_in.total_amount)
            return await self.update(db=db, db_obj=db_obj, obj_in=update_schema)
        else:
            # Create new
            return await self.create(db=db, obj_in=obj_in, collection_id=collection_id)


student_collection = CRUDStudentCollection()
