import uuid
from typing import List, Optional
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collection_news import CollectionNews
from app.schemas.collection_news import CollectionNewsCreate, CollectionNewsUpdate


class CRUDCollectionNews:
    async def get(self, db: AsyncSession, id: uuid.UUID) -> Optional[CollectionNews]:
        result = await db.execute(
            select(CollectionNews).filter(CollectionNews.id == id)
        )
        return result.scalars().first()

    async def get_multi_by_collection(
        self,
        db: AsyncSession,
        *,
        collection_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[CollectionNews]:
        result = await db.execute(
            select(CollectionNews)
            .filter(CollectionNews.collection_id == collection_id)
            .order_by(CollectionNews.date.desc())  # Sort by date descending
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: CollectionNewsCreate,
        collection_id: uuid.UUID,
        author_id: str
    ) -> CollectionNews:
        db_obj = CollectionNews(
            **obj_in.dict(),
            collection_id=collection_id,
            author_id=author_id,
            date=datetime.now()  # Ustaw datę automatycznie
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: CollectionNews, obj_in: CollectionNewsUpdate
    ) -> CollectionNews:
        update_data = obj_in.dict(exclude_unset=True)
        # Zazwyczaj tylko 'content' będzie aktualizowany
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        # Ewentualnie zaktualizuj datę modyfikacji, jeśli dodasz takie pole
        # db_obj.modified_date = datetime.now()
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(
        self, db: AsyncSession, *, id: uuid.UUID
    ) -> Optional[CollectionNews]:
        db_obj = await self.get(db=db, id=id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
        return db_obj


collection_news = CRUDCollectionNews()
