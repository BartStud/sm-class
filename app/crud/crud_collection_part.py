import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collection_part import CollectionPart
from app.schemas.collection_part import CollectionPartCreate, CollectionPartUpdate


class CRUDCollectionPart:
    async def get(self, db: AsyncSession, id: uuid.UUID) -> Optional[CollectionPart]:
        result = await db.execute(
            select(CollectionPart).filter(CollectionPart.id == id)
        )
        return result.scalars().first()

    async def get_multi_by_collection(
        self,
        db: AsyncSession,
        *,
        collection_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[CollectionPart]:
        result = await db.execute(
            select(CollectionPart)
            .filter(CollectionPart.collection_id == collection_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: CollectionPartCreate,
        collection_id: uuid.UUID
    ) -> CollectionPart:
        db_obj = CollectionPart(**obj_in.dict(), collection_id=collection_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: CollectionPart, obj_in: CollectionPartUpdate
    ) -> CollectionPart:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(
        self, db: AsyncSession, *, id: uuid.UUID
    ) -> Optional[CollectionPart]:
        db_obj = await self.get(db=db, id=id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
        return db_obj  # Zwraca usunięty obiekt lub None


collection_part = CRUDCollectionPart()
