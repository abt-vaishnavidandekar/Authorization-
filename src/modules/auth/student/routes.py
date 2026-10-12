
from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from configs.database import get_db
from modules.auth.student.functions import register_student, get_student_profile, update_student
from modules.auth.student.interfaces import StudentCreate, StudentUpdate
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
async def get_student(
    current_user: Student = Depends(get_current_user),
):
    return await get_student_profile(current_user=current_user)



@student_router.put("/stu_update/{user_id}")
async def update(
    user_id : int,
    first_name: str | None = Form(default=None),
    last_name: str | None = Form(default=None),
    age: int | None = Form(default=None),
    email: str | None = Form(default=None),
    ph_no: str | None = Form(default=None),
    profile_image: UploadFile | None = File(default=None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = StudentUpdate(
        **{
            key: value
            for key, value in {
                "first_name": first_name,
                "last_name": last_name,
                "age": age,
                "email": email,
                "ph_no": ph_no,
            }.items()
            if value is not None
        }
    )

    return await update_student(
        user_id=user_id,
        data=data,
        current_user=current_user,
        db=db,
        profile_image=profile_image,
    )
