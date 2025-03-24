from fastapi import APIRouter, HTTPException, status, Response
from sqlalchemy import select

from app.dependencies import CurrentUserDep, DatabaseDep
from app.models import Child
from app.schema.child import ChildCreate, ChildDetailResponse, ChildOut, ChildUpdate

router = APIRouter()


@router.get(
    "/children/{child_id}",
    response_model=ChildDetailResponse,
)
async def get_child(child_id: str, db: DatabaseDep, _: CurrentUserDep):
    query = select(Child).where(Child.id == child_id)
    result = await db.execute(query)
    child = result.scalar_one_or_none()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    return child


@router.post(
    "/current/children", response_model=ChildOut, status_code=status.HTTP_201_CREATED
)
async def add_child(
    child: ChildCreate,
    current: CurrentUserDep,
    db: DatabaseDep,
):
    token_data, _ = current
    new_child = Child(
        avatar=child.avatar,
        first_name=child.firstName,
        last_name=child.lastName,
        birth_date=child.birthDate,
        parent_id=token_data["sub"],
    )
    db.add(new_child)
    await db.commit()
    await db.refresh(new_child)
    return new_child


@router.put("/children/{child_id}", response_model=ChildOut)
async def edit_child(
    child_id: str,
    child_update: ChildUpdate,
    current: CurrentUserDep,
    db: DatabaseDep,
):
    token_data, _ = current
    query = select(Child).where(
        Child.id == child_id, Child.parent_id == token_data["sub"]
    )
    result = await db.execute(query)
    child = result.scalar_one_or_none()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    if child_update.avatar is not None:
        child.avatar = child_update.avatar
    if child_update.firstName is not None:
        child.first_name = child_update.firstName
    if child_update.lastName is not None:
        child.last_name = child_update.lastName
    if child_update.birthDate is not None:
        child.birth_date = child_update.birthDate
    await db.commit()
    await db.refresh(child)
    return child


@router.delete("/children/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_child(
    child_id: str,
    current: CurrentUserDep,
    db: DatabaseDep,
):
    token_data, _ = current
    query = select(Child).where(
        Child.id == child_id, Child.parent_id == token_data["sub"]
    )
    result = await db.execute(query)
    child = result.scalar_one_or_none()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    await db.delete(child)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
