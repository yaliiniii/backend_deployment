from pydantic import BaseModel, EmailStr


class DoctorBase(BaseModel):
    name: str
    email: EmailStr
    license_number: str
    specialization: str
    profile_image: str


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
