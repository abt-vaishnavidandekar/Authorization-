
from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from configs.database import get_db
from modules.auth.student.functions import register_student
from modules.auth.student.interfaces import StudentCreate
from modules.auth.student.models import Student
from utils.role import get_current_user

student_router = APIRouter(tags=["Student"])


@student_router.post("/register")
async def student_register(
    first_name: str = Form(...),
    last_name: str = Form(...),
    age: int = Form(...),
    ph_no: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    profile_image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    data = StudentCreate(
        first_name=first_name,
        last_name=last_name,
        age=age,
        ph_no=ph_no,
        email=email,
        password=password,
    )

    student = await register_student(
        data=data,
        profile_image=profile_image,
        db=db,
    )

    return {
        "message": "Student registered successfully",
        "id": student.id,
        "email": student.email,
        "profile_image": student.profile_image,
    }


@student_router.get("/me")
async def get_student_profile(
    current_user: Student = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "first_name": current_user.first_name,
        "email": current_user.email,
    }

