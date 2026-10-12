
from fastapi import HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.auth.student.interfaces import StudentUpdate
from modules.auth.student.models import Student
from utils.file_handler import save_profile_image
from utils.security import hash_password
from utils.validators import check_name, validate_email, validate_password

from .interfaces import AdminCreate, AdminUpdate
from .models import Admin


async def register_admin(data: AdminCreate, db: AsyncSession):
    result = await db.execute(
        select(Admin).where(Admin.email == data.email)
    )

    if result.scalar_one_or_none():
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content = {
                "success" : False,
                "msg" : "Admin already Exists"
            }
        )

    admin = Admin(
        first_name=check_name(data.first_name),
        last_name=check_name(data.last_name),
        email=validate_email(data.email),
        password_hash=hash_password(validate_password(data.password)),
    )

    db.add(admin)
    await db.commit()
    await db.refresh(admin)

    return admin


async def get_all_students(db: AsyncSession):
    result = await db.execute(
        select(Student).order_by(Student.id)
    )
    return result.scalars().all()


async def get_student_by_id(student_id: int, db: AsyncSession):
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )

    student = result.scalar_one_or_none()

    if student is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content = {
                "success" : False,
                "msg" : "Student not found"
            }
        )

    return student



async def update_admin(user_id: int, data: AdminUpdate, current_admin: Admin, db: AsyncSession):

    if current_admin.id == user_id:
        admin_to_update = current_admin
    else:
        admin_to_update = await db.get(Admin, user_id)
        if not admin_to_update:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "success" : False,
                    "msg" : "Admin profile not found"
                }
              
            )

  
    updates = data.model_dump(exclude_unset=True, exclude_none=True)
  
    protected_fields = {"id", "password_hash"}
    
    for field, value in updates.items():
        if field not in protected_fields and hasattr(admin_to_update, field):
            setattr(admin_to_update, field, value)

    await db.commit()
    await db.refresh(admin_to_update)

    return {
        "success": True,
        "message": "Admin profile updated successfully",
        "data": {
            "id": admin_to_update.id,
            "email": admin_to_update.email,
            "first_name": admin_to_update.first_name,
            "last_name": admin_to_update.last_name,
        }
    }



async def update_user(
    user_id: int,
    data: StudentUpdate,
    current_user,
    db: AsyncSession,
    profile_image: UploadFile | None = None,
):
    if isinstance(current_user, Student):
        if current_user.id != user_id:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "success" : False,
                    "msg" : "You can update only your own profile"
                }
            )
        user = current_user

    elif isinstance(current_user, Admin):
        if current_user.id == user_id:
            user = current_user
        else:
            user = await db.get(Student, user_id)

            if not user:
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={
                        "success" : False,
                        "msg" : "Student not found"
                        }
                    )

    else:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "success" : False,
                "msg" : "Permission denied"
                }
            )

    updates = data.model_dump(exclude_unset=True, exclude_none=True)

    allowed_fields = ("first_name", "last_name", "email")
    if isinstance(user, Student):
        allowed_fields += ("age", "ph_no")

    for field in allowed_fields:
        if field in updates:
            setattr(user, field, updates[field])

    if profile_image is not None:
        if not hasattr(user, "profile_image"):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success" : False,
                    "msg" : "Profile image is not supported for this account"
                    }
                )
        
        user.profile_image = await save_profile_image(profile_image)

    await db.commit()
    await db.refresh(user)

    return {"message": "data updated successfully"}

    
async def delete_student(student_id: int, db: AsyncSession):
    student = await db.get(Student, student_id)

    if not student:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success" : False,
                "msg": "Student not found"
            }
    )

    await db.delete(student)
    await db.commit()

    return {"message": "Student deleted successfully"}

