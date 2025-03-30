import uuid
from typing import List, Optional
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.class_collector import ClassCollector
from app.schemas.class_collector import ClassCollectorCreate, ClassCollectorUpdate


class CRUDClassCollector:
    async def get(self, db: AsyncSession, id: uuid.UUID) -> Optional[ClassCollector]:
        result = await db.execute(
            select(ClassCollector).filter(ClassCollector.id == id)
        )
        return result.scalars().first()

    async def get_multi_by_class(
        self,
        db: AsyncSession,
        *,
        class_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        only_active: bool = False
    ) -> List[ClassCollector]:
        statement = select(ClassCollector).filter(ClassCollector.class_id == class_id)
        if only_active:
            statement = statement.filter(
                (ClassCollector.end == None) | (ClassCollector.end > datetime.now())
            )
        statement = statement.offset(skip).limit(limit)
        result = await db.execute(statement)
        return result.scalars().all()

    async def create_for_class(
        self, db: AsyncSession, *, obj_in: ClassCollectorCreate, class_id: uuid.UUID
    ) -> ClassCollector:
        start_date = obj_in.start if obj_in.start else datetime.now()
        db_obj = ClassCollector(
            parent_id=obj_in.parent_id,
            class_id=class_id,
            start=start_date,
            end=obj_in.end,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: ClassCollector, obj_in: ClassCollectorUpdate
    ) -> ClassCollector:
        update_data = obj_in.dict(exclude_unset=True)
        # Głównie do ustawiania daty 'end'
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(
        self, db: AsyncSession, *, id: uuid.UUID
    ) -> Optional[ClassCollector]:
        """Usuwa przypisanie skarbnika do klasy. Rozważ użycie update z datą 'end'."""
        db_obj = await self.get(db=db, id=id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
        return db_obj


class_collector = CRUDClassCollector()
