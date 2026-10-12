
from fastapi import UploadFile, status
from sqlalchemy import select
from modules.auth.admin.models import Admin
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from .interfaces import StudentUpdate

from utils.file_handler import save_profile_image
from utils.security import hash_password
from utils.validators import check_name, check_phone, validate_email, validate_password

from .interfaces import StudentCreate
from .models import Student


async def register_student(
    data: StudentCreate,
    profile_image: UploadFile,
    db: AsyncSession,
):
    image_path = await save_profile_image(profile_image)

    student = Student(
        first_name=check_name(data.first_name),
        last_name=data.last_name,
        email=validate_email(data.email),
        ph_no=check_phone(data.ph_no),
        age=data.age,
        password_hash=hash_password(validate_password(data.password)),
        profile_image=image_path,
    )

    db.add(student)
    await db.commit()
    await db.refresh(student)

    return student




async def get_student_profile(
    current_user: Student,
):
    return {
        "id": current_user.id,
        "first_name": current_user.first_name,
        "email": current_user.email,
    }



async def update_student(
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
