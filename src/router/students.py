from fastapi import APIRouter

from modules.auth.student.routes import student_router

router = APIRouter(prefix="/student")

router.include_router(student_router)
