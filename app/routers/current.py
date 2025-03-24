from typing import List
from io import BytesIO

from fastapi import APIRouter, File, HTTPException, UploadFile
from sqlalchemy import select

from app.dependencies import CurrentUserDep, DatabaseDep
from app.models import Child
from app.schema.user import UserResponse, UserUpdate
from app.schema.child import ChildOut
from app.services import keycloak_admin
from app.services.minio_api import minio_put_object

router = APIRouter()


@router.get("/current", response_model=UserResponse)
async def get_current_user_endpoint(current: CurrentUserDep):
    token_data, _ = current
    return {
        "id": token_data["sub"],
        "avatar": token_data.get("avatar"),
        "firstName": token_data.get("firstName"),
        "lastName": token_data.get("lastName"),
        "username": token_data.get("username"),
        "email": token_data.get("email"),
        "role": token_data.get("role"),
    }


@router.patch("/current", response_model=UserResponse)
async def edit_current_user(update: UserUpdate, current: CurrentUserDep):
    token_data, _ = current
    user_id = token_data["sub"]
    update_data = {}
    if update.avatar is not None:
        update_data["avatar"] = update.avatar
    if update.firstName is not None:
        update_data["firstName"] = update.firstName
    if update.lastName is not None:
        update_data["lastName"] = update.lastName
    if update.username is not None:
        update_data["username"] = update.username
    if update.email is not None:
        update_data["email"] = update.email
    try:
        keycloak_admin.update_user(user_id, update_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    updated_user = keycloak_admin.get_user(user_id)
    return updated_user


@router.post("/current/avatar", response_model=UserResponse)
async def upload_avatar(current: CurrentUserDep, file: UploadFile = File(...)):
    token_data, _ = current
    user_id = token_data["sub"]

    file_extension = file.filename.split(".")[-1]
    object_name = f"avatars/{user_id}.{file_extension}"
    file_content = await file.read()

    try:
        file_data = BytesIO(file_content)
        new_avatar_url = minio_put_object(object_name, file_data)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error uploading file: {str(e)}"
        ) from e

    try:
        keycloak_admin.update_user(user_id, {"avatar": new_avatar_url})
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error updating avatar in Keycloak: {str(e)}"
        ) from e
    updated_user = keycloak_admin.get_user(user_id)
    return updated_user


@router.get("/current/children", response_model=List[ChildOut])
async def get_children(current: CurrentUserDep, db: DatabaseDep):
    token_data, _ = current
    query = select(Child).where(Child.parent_id == token_data["sub"])
    result = await db.execute(query)
    children = result.scalars().all()
    return children
