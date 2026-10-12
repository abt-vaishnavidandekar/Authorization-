import secrets

from pydantic import BaseModel, Field
from redis.asyncio import Redis


class OTPRequest(BaseModel):
    email: str

class OTPVerifyRequest(BaseModel):
    otp: str = Field(pattern=r"^\d{6}$")

class PasswordResetRequest(BaseModel):
    otp: str = Field(pattern=r"^\d{6}$")
    new_password: str = Field(min_length=8, max_length=72)




redis = Redis.from_url(
    "redis://localhost:6379/0",
    decode_responses=True,
)


async def generate_otp(email: str) -> str:
    otp = f"{secrets.randbelow(1_000_000):06d}"

    await redis.set(
        f"password_reset:{email.lower().strip()}",
        otp,
        ex=300,
    )

    return otp


async def verify_otp(email: str, otp: str) -> bool:
    key = f"password_reset:{email.lower().strip()}"
    stored_otp = await redis.get(key)

    if stored_otp is None or not secrets.compare_digest(stored_otp, otp):
        return False

    await redis.delete(key)
    return True