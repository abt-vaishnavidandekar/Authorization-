
from fastapi import APIRouter

from modules.auth.admin.routes import admin_router

router = APIRouter(prefix="/admin")

router.include_router(admin_router)
