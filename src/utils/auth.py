from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.auth.admin.models import Admin
from modules.auth.student.models import Student
from utils.jwt import create_access_token, create_refresh_token
from utils.security import verify_password


from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    Response,
)
from jose import JWTError, jwt
from .otp_service import OTPRequest, PasswordResetRequest
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from configs.database import get_db
from utils.jwt import ALGORITHM, SECRET_KEY
from utils.otp_service import generate_otp, verify_otp
from utils.role import get_current_user
from utils.security import hash_password


async def login_user(email: str, password: str, db: AsyncSession):
    for model, role in (
        (Admin, "admin"),
        (Student, "student"),
    ):
        result = await db.execute(
            select(model).where(model.email == email.lower().strip())
        )
        user = result.scalar_one_or_none()

        if user and verify_password(password, user.password_hash):
            return {
                "access_token": create_access_token(user.id, role),
                "refresh_token": create_refresh_token(user.id, role),
                "token_type": "bearer",
                "role": role,
            }

    raise HTTPException(
        status_code=401,
        detail="Invalid email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )



auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=1)


@auth_router.post("/login")
async def login(
    data: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    tokens = await login_user(
        email=data.email,
        password=data.password,
        db=db,
    )

    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=False, 
        samesite="lax",
        max_age=15 * 60,
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=False,  
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
        path="/auth",
    )

    return {
        "message": "Login successful",
        "role": tokens["role"],
    }



@auth_router.post("/refresh")
async def refresh_access_token(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Refresh token cookie missing",
        )

    try:
        payload = jwt.decode(
            refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token",
            )

        user_id = int(payload["sub"])
        role = payload.get("role")

        if role not in ("admin", "student"):
            raise HTTPException(
                status_code=401,
                detail="Invalid user role",
            )

    except (JWTError, ValueError, KeyError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token",
        )

    model = Admin if role == "admin" else Student

    result = await db.execute(
        select(model).where(model.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    new_access_token = create_access_token(user.id, role)

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=False,  
        samesite="lax",
        max_age=15 * 60,
        path="/",
    )

    return {"message": "Access token refreshed"}



@auth_router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True,
        samesite="lax",
    )

    response.delete_cookie(
        key="refresh_token",
        path="/auth",
        httponly=True,
        samesite="lax",
    )

    return {"message": "Logout successful"}




@auth_router.post("/password/request-otp")
async def request_password_otp(
    data: OTPRequest,
    db: AsyncSession = Depends(get_db),
):
    email = data.email.lower().strip()

    student = await db.scalar(
        select(Student).where(Student.email == email)
    )
    admin = await db.scalar(
        select(Admin).where(Admin.email == email)
    )

    if not student and not admin:
        raise HTTPException(404, "Account not found")

    otp = await generate_otp(email)

    return {
        "message": "OTP generated successfully",
        "email": email,
        "otp": otp,
        "expires_in_seconds": 300,
    }



@auth_router.post("/password/reset")
async def reset_password(
    data: PasswordResetRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    email = current_user.email.strip().lower()

    if not await verify_otp(email, data.otp):
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP",
        )

    if not isinstance(current_user, (Student, Admin)):
        raise HTTPException(403, "Permission denied")

    current_user.password_hash = hash_password(data.new_password)

    await db.commit()

    return {"message": "Password updated successfully"}
