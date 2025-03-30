from fastapi import APIRouter

from app.routers import classes, collections, me

api_router = APIRouter()
api_router.include_router(
    classes.router, prefix="/classes", tags=["Classes & Assignments"]
)
api_router.include_router(
    collections.router, prefix="/collections", tags=["Collections & Participation"]
)
api_router.include_router(me.router, prefix="/me", tags=["Current User"])
