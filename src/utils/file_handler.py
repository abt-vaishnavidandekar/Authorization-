import uuid
from pathlib import Path

from fastapi import UploadFile, status
from fastapi.responses import JSONResponse

PROFILE_DIR = Path("media/profiles")
MAX_IMAGE_SIZE = 2 * 1024 * 1024  

ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


async def save_profile_image(image: UploadFile) -> str:

    if image.content_type not in ALLOWED_TYPES:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content = {
                "success" : False,
                "msg" : "Upload image in jpg, png.."
            }
        )

    image_data = await image.read(MAX_IMAGE_SIZE + 1)

    if not image_data:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content = {
                "success" : False,
                "msg" : "Upload image is empty"
            }
        )

    if len(image_data) > MAX_IMAGE_SIZE:
        return JSONResponse(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            content = {
                "success" : False,
                "msg" : "Upload image must be 2MB or smaller"
            }
        )

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    extension = ALLOWED_TYPES[image.content_type]
    filename = f"{uuid.uuid4().hex}{extension}"
    file_path = PROFILE_DIR / filename

    file_path.write_bytes(image_data)

    return file_path.as_posix()
