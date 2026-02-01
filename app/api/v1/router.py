from fastapi import APIRouter
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import rooms
from app.api.v1.endpoints import polls
from app.api.v1.endpoints import pickers

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(rooms.router)
router.include_router(polls.router)
router.include_router(pickers.router)


