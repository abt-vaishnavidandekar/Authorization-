from pydantic import BaseModel, Field


class StudentCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    age: int = Field(gt=10, lt=50)
    ph_no: str
    email: str
    password: str = Field(min_length=8, max_length=128)


class StudentUpdate(BaseModel):

    first_name: str | None = Field(default=None, min_length=1)
    last_name: str | None = Field(default=None, min_length=1)
    age: int | None = Field(default=None, ge=1, le=120)
    email: str | None = None
    ph_no: str | None = None


class StudentResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    ph_no: str
    age: int
    profile_image: str

    model_config = {"from_attributes": True}

