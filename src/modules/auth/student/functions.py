
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

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

