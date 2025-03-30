import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.school_class import SchoolClass
from app.schemas.school_class import SchoolClassCreate, SchoolClassUpdate


class CRUDSchoolClass:
    async def get(self, db: AsyncSession, id: uuid.UUID) -> Optional[SchoolClass]:
        result = await db.execute(select(SchoolClass).filter(SchoolClass.id == id))
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[SchoolClass]:
        result = await db.execute(select(SchoolClass).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(
        self, db: AsyncSession, *, obj_in: SchoolClassCreate
    ) -> SchoolClass:
        db_obj = SchoolClass(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: SchoolClass, obj_in: SchoolClassUpdate
    ) -> SchoolClass:
        update_data = obj_in.dict(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: uuid.UUID) -> Optional[SchoolClass]:
        db_obj = await self.get(db=db, id=id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
        return db_obj  # Return the deleted object or None


school_class = CRUDSchoolClass()
