from pydantic import BaseModel, EmailStr
from typing import Optional


class DoctorBase(BaseModel):
    name: str
    email: EmailStr
    license_number: str
    specialization: Optional[str] = None
    profile_image: Optional[str] = None


class DoctorCreate(DoctorBase):
    password: str


class DoctorLogin(BaseModel):
    email: EmailStr
    password: str


class DoctorResponse(DoctorBase):
    id: int
    is_approved: bool = False

    class Config:
        from_attributes = True
