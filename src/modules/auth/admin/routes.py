from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from configs.database import get_db
from modules.auth.student.interfaces import StudentUpdate
from utils.role import get_current_user, require_role

from .functions import (
    delete_student,
    get_all_students,
    get_student_by_id,
    register_admin,
    update_admin,
    update_user,
)
from .interfaces import AdminCreate, AdminUpdate
from .models import Admin

admin_router = APIRouter(tags=["Admin"])


@admin_router.post("/register")
async def admin_register(data: AdminCreate, db: AsyncSession = Depends(get_db)):
    admin = await register_admin(data, db)

    return {
        "message": "Admin registered successfully",
        "id": admin.id,
        "first_name": admin.first_name,
        "last_name": admin.last_name,
        "email": admin.email,
    }

@admin_router.get("/me")
async def get_admin_profile(
    current_user: Admin = Depends(require_role("admin")),
):
    return {
        "id": current_user.id,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "role": "admin",
    }

@admin_router.get("/students")
async def student_data(current_admin=Depends(require_role("admin")),db: AsyncSession=Depends(get_db)):
    return await get_all_students(db=db)

@admin_router.get("/students/{student_id}")
async def get_student(
    student_id: int,
    current_admin=Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    student = await get_student_by_id(student_id, db)

    return {
        "id": student.id,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "email": student.email,
        "age": student.age,
        "ph_no": student.ph_no,
        "profile_image": student.profile_image,
    }

@admin_router.patch("/admin_update/{admin_id}}")
async def admin_update(
    admin_id : int,
    data: AdminUpdate,
    current_admin: Admin = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    return await update_admin(admin_id=admin_id, data=data, admin=current_admin, db=db)



@admin_router.put("/stu_update/{student_id}")
async def update(
    student_id: int,
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

    return await update_user(
        student_id=student_id,
        data=data,
        current_user=current_user,
        db=db,
        profile_image=profile_image,
    )



@admin_router.delete("/students/{student_id}")
async def remove_student(
    student_id: int,
    current_admin=Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    return await delete_student(student_id, db)
