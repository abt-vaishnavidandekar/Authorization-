
from fastapi import APIRouter

from utils.auth import auth_router

router = APIRouter(prefix="/admin")

router.include_router(auth_router)

