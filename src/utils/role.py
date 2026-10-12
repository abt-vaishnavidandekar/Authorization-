from fastapi import Cookie, Depends, status
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from configs.database import get_db
from modules.auth.admin.models import Admin
from modules.auth.student.models import Student
from utils.jwt import ALGORITHM, SECRET_KEY


async def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    if not access_token:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"success": False, 
                     "msg": "Access token Missing"
                     }
                )

    try:
        payload = jwt.decode(
            access_token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        if payload.get("type") != "access":
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"success": False, 
                         "msg": "Invalid access token"
                         }
                    )

        user_id = int(payload["sub"])
        role = payload.get("role")

        if role not in ("student", "admin"):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"success": False, 
                         "msg": "Invalid Role"
                         }
                    )

    except (JWTError, ValueError, KeyError, TypeError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"success": False, 
                     "msg": "Invalid or Expired Access token"
                     }
                 )

    model = Admin if role == "admin" else Student

    result = await db.execute(
        select(model).where(model.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, 
                    "msg": "User not found"}
        )

    return user




def require_role(required_role: str):
    if required_role not in ("student", "admin"):
       return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, 
                     "msg": "Invalid configuration role"}
        )

    async def role_checker(
        current_user=Depends(get_current_user),
        access_token: str | None = Cookie(default=None),
    ):

        try:
            payload = jwt.decode(
                access_token,
                SECRET_KEY,
                algorithms=[ALGORITHM],
            )
        except (JWTError, TypeError):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"success": False, 
                        "msg": "Invalid or Expired Access token"}
            )

        if payload.get("role") != required_role:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"success": False, 
                        "msg": "Permission denied"}
            )

        return current_user

    return role_checker
