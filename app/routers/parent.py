from fastapi import APIRouter, HTTPException

from app.dependencies import CurrentUserDep
from app.schema.child import ParentOut
from app.services import keycloak_admin

router = APIRouter()


@router.get("/parent/{parent_id}", response_model=ParentOut)
async def get_parent(parent_id: str, _: CurrentUserDep):
    user_data = keycloak_admin.get_user(parent_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="Parent not found")
    return user_data
