from typing import Annotated
from fastapi import Depends

from app.core.security import verify_token


async def get_current_user(user=Depends(verify_token)):
    return user


CurrentUserDep = Annotated[dict, Depends(get_current_user)]
