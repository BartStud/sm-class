import uuid
from typing import List, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Body

from app import crud, schemas, models
from app.dependencies.db import DatabaseDep
from app.dependencies.auth import CurrentUserDep

router = APIRouter()


@router.post(
    "/", response_model=schemas.Collection, status_code=status.HTTP_201_CREATED
)
async def create_collection(
    *,
    db: DatabaseDep,
    collection_in: schemas.CollectionCreate,
    current_user: CurrentUserDep,  # User creating the collection
) -> Any:
    """
    Create new collection.
    """
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

    # Optional: Check if the class_id exists
    # school_class = await crud.school_class.get(db=db, id=uuid.UUID(collection_in.class_id)) # Potential UUID conversion error if class_id isn't UUID
    # if not school_class:
    #    raise HTTPException(status_code=404, detail=f"School Class with id {collection_in.class_id} not found")

    # Optional: Check if current_user is allowed to create collection for this class_id
    # (e.g., are they a ClassCollector for this class?)

    collection = await crud.collection.create(
        db=db, obj_in=collection_in, created_by_id=user_id
    )

    # TODO: Potentially auto-create StudentCollection entries here based on ClassStudents
    # students_in_class = await crud.class_student.get_multi_by_class(db=db, class_id=collection.class_id)
    # for student in students_in_class:
    #     if student.end is None or student.end > datetime.now(): # Only active students
    #        # Calculate student amount based on collection.payment_type, total_amount, etc.
    #        student_amount = ...
    #        student_collection_in = schemas.StudentCollectionCreate(student_id=student.student_id, total_amount=student_amount)
    #        await crud.student_collection.create_for_collection(db=db, obj_in=student_collection_in, collection_id=collection.id)

    return collection


@router.get("/", response_model=List[schemas.Collection])
async def read_collections(
    db: DatabaseDep,
    current_user: CurrentUserDep,
    skip: int = 0,
    limit: int = 100,
    class_id: Optional[str] = None,  # Filter by class_id (which is string in model)
) -> Any:
    """
    Retrieve collections. Can be filtered by class_id.
    """
    if class_id:
        # Need to ensure class_id format matches what's stored if it's supposed to be UUID
        collections = await crud.collection.get_multi_by_class(
            db, class_id=class_id, skip=skip, limit=limit
        )
    else:
        # Add logic here if users should only see collections relevant to them
        collections = await crud.collection.get_multi(db, skip=skip, limit=limit)
    return collections


@router.get("/{collection_id}", response_model=schemas.Collection)
async def read_collection(
    *,
    db: DatabaseDep,
    collection_id: uuid.UUID,
    current_user: CurrentUserDep,
) -> Any:
    """
    Get collection by ID.
    """
    collection = await crud.collection.get(db=db, id=collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    # Add permission check: Is user part of the class associated with collection?
    return collection


@router.put("/{collection_id}", response_model=schemas.Collection)
async def update_collection(
    *,
    db: DatabaseDep,
    collection_id: uuid.UUID,
    collection_in: schemas.CollectionUpdate,
    current_user: CurrentUserDep,
) -> Any:
    """
    Update a collection.
    """
    collection = await crud.collection.get(db=db, id=collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    user_id = current_user.get("sub")
    # Add permission check: e.g., is user the creator or a collector for the class?
    # if collection.created_by != user_id and not user_is_collector_for_class(user_id, collection.class_id):
    #    raise HTTPException(status_code=403, detail="Not enough permissions")

    updated_collection = await crud.collection.update(
        db=db, db_obj=collection, obj_in=collection_in
    )
    return updated_collection


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(
    *,
    db: DatabaseDep,
    collection_id: uuid.UUID,
    current_user: CurrentUserDep,
) -> None:
    """
    Delete a collection.
    """
    collection = await crud.collection.get(db=db, id=collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    user_id = current_user.get("sub")
    # Add permission check: e.g., creator or admin?
    # if collection.created_by != user_id and not user_is_admin(user_id):
    #    raise HTTPException(status_code=403, detail="Not enough permissions")

    await crud.collection.remove(db=db, id=collection_id)
    return None


# --- Endpoints for related models (Parts, News, StudentCollections) ---


# Collection Parts
@router.post(
    "/{collection_id}/parts/",
    response_model=schemas.CollectionPart,
    status_code=status.HTTP_201_CREATED,
)
async def create_collection_part(
    *,
    db: DatabaseDep,
    collection_id: uuid.UUID,
    part_in: schemas.CollectionPartCreate,
    current_user: CurrentUserDep,  # Check permissions
) -> Any:
    """
    Add a new part to a collection.
    """
    collection = await crud.collection.get(db=db, id=collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    # Add permission check (e.g., creator/collector)
    part = await crud.collection_part.create(
        db=db, obj_in=part_in, collection_id=collection_id
    )
    return part


@router.get("/{collection_id}/parts/", response_model=List[schemas.CollectionPart])
async def list_collection_parts(
    *,
    db: DatabaseDep,
    collection_id: uuid.UUID,
    current_user: CurrentUserDep,  # Check permissions
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    List parts for a specific collection.
    """
    collection = await crud.collection.get(db=db, id=collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    # Add permission checks
    parts = await crud.collection_part.get_multi_by_collection(
        db=db, collection_id=collection_id, skip=skip, limit=limit
    )
    return parts


# TODO: Add PUT/DELETE endpoints for /collections/{collection_id}/parts/{part_id}


# Collection News
@router.post(
    "/{collection_id}/news/",
    response_model=schemas.CollectionNews,
    status_code=status.HTTP_201_CREATED,
)
async def create_collection_news(
    *,
    db: DatabaseDep,
    collection_id: uuid.UUID,
    news_in: schemas.CollectionNewsCreate,
    current_user: CurrentUserDep,  # Check permissions
) -> Any:
    """
    Add news to a collection.
    """
    collection = await crud.collection.get(db=db, id=collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

    # Add permission checks (creator, collector, maybe parent/student in class?)
    news = await crud.collection_news.create(
        db=db, obj_in=news_in, collection_id=collection_id, author_id=user_id
    )
    return news


@router.get("/{collection_id}/news/", response_model=List[schemas.CollectionNews])
async def list_collection_news(
    *,
    db: DatabaseDep,
    collection_id: uuid.UUID,
    current_user: CurrentUserDep,  # Check permissions
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    List news items for a specific collection.
    """
    collection = await crud.collection.get(db=db, id=collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    # Add permission checks
    news_list = await crud.collection_news.get_multi_by_collection(
        db=db, collection_id=collection_id, skip=skip, limit=limit
    )
    return news_list


# TODO: Add PUT/DELETE endpoints for /collections/{collection_id}/news/{news_id} (if needed)


# Student Collections (Participation)
@router.get(
    "/{collection_id}/students/", response_model=List[schemas.StudentCollection]
)
async def list_students_in_collection(
    *,
    db: DatabaseDep,
    collection_id: uuid.UUID,
    current_user: CurrentUserDep,  # Check permissions (creator, collector?)
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    List students participating in a specific collection and their amounts.
    """
    collection = await crud.collection.get(db=db, id=collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    # Add permission checks
    student_participations = await crud.student_collection.get_multi_by_collection(
        db=db, collection_id=collection_id, skip=skip, limit=limit
    )
    return student_participations


@router.put("/{collection_id}/parts/{part_id}", response_model=schemas.CollectionPart)
async def update_collection_part(
    *,
    db: DatabaseDep,
    collection_id: uuid.UUID,
    part_id: uuid.UUID,
    part_in: schemas.CollectionPartUpdate,
    current_user: CurrentUserDep,  # Sprawdź uprawnienia (np. creator/collector)
) -> Any:
    """
    Update a collection part.
    """
    collection = await crud.collection.get(db=db, id=collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    part = await crud.collection_part.get(db=db, id=part_id)
    if not part or part.collection_id != collection_id:
        raise HTTPException(
            status_code=404, detail="Collection Part not found for this collection"
        )

    # TODO: Sprawdź uprawnienia (czy user może edytować tę zbiórkę?)

    updated_part = await crud.collection_part.update(db=db, db_obj=part, obj_in=part_in)
    return updated_part


@router.delete(
    "/{collection_id}/parts/{part_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_collection_part(
    *,
    db: DatabaseDep,
    collection_id: uuid.UUID,
    part_id: uuid.UUID,
    current_user: CurrentUserDep,  # Sprawdź uprawnienia
) -> None:
    """
    Delete a collection part.
    """
    collection = await crud.collection.get(db=db, id=collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    part = await crud.collection_part.get(db=db, id=part_id)
    if not part or part.collection_id != collection_id:
        raise HTTPException(
            status_code=404, detail="Collection Part not found for this collection"
        )

    # TODO: Sprawdź uprawnienia

    await crud.collection_part.remove(db=db, id=part_id)
    return None


# --- Collection News Endpoints ---

# POST /{collection_id}/news/ - Już istnieje
# GET /{collection_id}/news/ - Już istnieje


@router.put("/{collection_id}/news/{news_id}", response_model=schemas.CollectionNews)
async def update_collection_news_item(
    *,
    db: DatabaseDep,
    collection_id: uuid.UUID,
    news_id: uuid.UUID,
    news_in: schemas.CollectionNewsUpdate,  # Zazwyczaj tylko 'content'
    current_user: CurrentUserDep,  # Sprawdź uprawnienia
) -> Any:
    """
    Update a news item associated with a collection.
    """
    collection = await crud.collection.get(db=db, id=collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    news_item = await crud.collection_news.get(db=db, id=news_id)
    if not news_item or news_item.collection_id != collection_id:
        raise HTTPException(
            status_code=404, detail="News item not found for this collection"
        )

    user_id = current_user.get("sub")
    # TODO: Sprawdź uprawnienia (np. czy user jest autorem LUB adminem/skarbnikiem)
    # if news_item.author_id != user_id and not user_is_admin_or_collector(...):
    #     raise HTTPException(status_code=403, detail="Not authorized to update this news item")

    updated_news = await crud.collection_news.update(
        db=db, db_obj=news_item, obj_in=news_in
    )
    return updated_news


@router.delete(
    "/{collection_id}/news/{news_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_collection_news_item(
    *,
    db: DatabaseDep,
    collection_id: uuid.UUID,
    news_id: uuid.UUID,
    current_user: CurrentUserDep,  # Sprawdź uprawnienia
) -> None:
    """
    Delete a news item associated with a collection.
    """
    collection = await crud.collection.get(db=db, id=collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    news_item = await crud.collection_news.get(db=db, id=news_id)
    if not news_item or news_item.collection_id != collection_id:
        raise HTTPException(
            status_code=404, detail="News item not found for this collection"
        )

    user_id = current_user.get("sub")
    # TODO: Sprawdź uprawnienia (np. autor LUB admin/skarbnik)
    # if news_item.author_id != user_id and not user_is_admin_or_collector(...):
    #     raise HTTPException(status_code=403, detail="Not authorized to delete this news item")

    await crud.collection_news.remove(db=db, id=news_id)
    return None


# --- Student Collection (Participation) Endpoints ---

# GET /{collection_id}/students/ - Już istnieje (lista)


@router.post(
    "/{collection_id}/students/",
    response_model=schemas.StudentCollection,
    status_code=status.HTTP_201_CREATED,
)
async def add_student_participation(
    *,
    db: DatabaseDep,
    collection_id: uuid.UUID,
    student_collection_in: schemas.StudentCollectionCreate,  # Zawiera student_id, total_amount
    current_user: CurrentUserDep,  # Sprawdź uprawnienia (np. collector/admin)
) -> Any:
    """
    Manually add a student's participation record to a collection.
    Useful if not automatically created or needs adjustment. Consider upsert logic.
    """
    collection = await crud.collection.get(db=db, id=collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    # TODO: Sprawdź uprawnienia (np. skarbnik/admin)
    # TODO: Sprawdź, czy student_id jest poprawnym ID (np. z Keycloak lub ClassStudent)
    # TODO: Rozważ sprawdzenie, czy student już nie uczestniczy, aby uniknąć duplikatów (zależy od logiki - create vs upsert)
    existing = await crud.student_collection.get(
        db=db, student_id=student_collection_in.student_id, collection_id=collection_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student participation record already exists for this collection.",
        )

    # Przypisz collection_id z URL
    participation = await crud.student_collection.create(
        db=db, obj_in=student_collection_in, collection_id=collection_id
    )
    return participation


@router.get(
    "/{collection_id}/students/{student_id}", response_model=schemas.StudentCollection
)
async def get_student_participation(
    *,
    db: DatabaseDep,
    collection_id: uuid.UUID,
    student_id: str,  # ID studenta (z Keycloak)
    current_user: CurrentUserDep,  # Sprawdź uprawnienia
) -> Any:
    """
    Get a specific student's participation details for a collection.
    """
    collection = await crud.collection.get(db=db, id=collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    # TODO: Sprawdź uprawnienia (np. skarbnik/admin LUB sam student/rodzic?)

    participation = await crud.student_collection.get(
        db=db, student_id=student_id, collection_id=collection_id
    )
    if not participation:
        raise HTTPException(
            status_code=404, detail="Student participation record not found"
        )

    return participation


@router.put(
    "/{collection_id}/students/{student_id}", response_model=schemas.StudentCollection
)
async def update_student_participation(
    *,
    db: DatabaseDep,
    collection_id: uuid.UUID,
    student_id: str,
    participation_in: schemas.StudentCollectionUpdate,  # Zazwyczaj tylko kwota 'total_amount'
    current_user: CurrentUserDep,  # Sprawdź uprawnienia (np. collector/admin)
) -> Any:
    """
    Update a student's participation details (e.g., the amount).
    """
    collection = await crud.collection.get(db=db, id=collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    # TODO: Sprawdź uprawnienia

    participation = await crud.student_collection.get(
        db=db, student_id=student_id, collection_id=collection_id
    )
    if not participation:
        raise HTTPException(
            status_code=404, detail="Student participation record not found"
        )

    updated_participation = await crud.student_collection.update(
        db=db, db_obj=participation, obj_in=participation_in
    )
    return updated_participation


@router.delete(
    "/{collection_id}/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_student_participation(
    *,
    db: DatabaseDep,
    collection_id: uuid.UUID,
    student_id: str,
    current_user: CurrentUserDep,  # Sprawdź uprawnienia (np. collector/admin)
) -> None:
    """
    Delete a student's participation record from a collection.
    """
    collection = await crud.collection.get(db=db, id=collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    # TODO: Sprawdź uprawnienia

    participation = await crud.student_collection.get(
        db=db, student_id=student_id, collection_id=collection_id
    )
    if not participation:
        raise HTTPException(
            status_code=404, detail="Student participation record not found"
        )

    await crud.student_collection.remove(
        db=db, student_id=student_id, collection_id=collection_id
    )
    return None
