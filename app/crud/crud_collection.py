import uuid
from typing import List, Optional
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collection import Collection
from app.schemas.collection import CollectionCreate, CollectionUpdate


class CRUDCollection:
    async def get(self, db: AsyncSession, id: uuid.UUID) -> Optional[Collection]:
        result = await db.execute(select(Collection).filter(Collection.id == id))
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Collection]:
        result = await db.execute(
            select(Collection)
            .order_by(Collection.creation_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_multi_by_class(
        self, db: AsyncSession, *, class_id: str, skip: int = 0, limit: int = 100
    ) -> List[Collection]:
        result = await db.execute(
            select(Collection)
            .filter(Collection.class_id == class_id)
            .order_by(Collection.creation_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create(
        self, db: AsyncSession, *, obj_in: CollectionCreate, created_by_id: str
    ) -> Collection:
        db_obj = Collection(
            **obj_in.dict(),
            created_by=created_by_id,
            creation_date=datetime.now()  # Ensure creation date is set
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: Collection, obj_in: CollectionUpdate
    ) -> Collection:
        update_data = obj_in.dict(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: uuid.UUID) -> Optional[Collection]:
        db_obj = await self.get(db=db, id=id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
        return db_obj


collection = CRUDCollection()
