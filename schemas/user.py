from pydantic import BaseModel, EmailStr
from typing import Optional, Any


class UserBase(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    phone: Optional[str] = None
    activity: Optional[str] = None
    years_smoked: Optional[int] = 0
    cigarettes_per_day: Optional[int] = 0
    target_quit_date: Optional[Any] = None
    reason_quitting: Optional[str] = None
    triggers: Optional[str] = None


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    age: Optional[int] = None
    phone: Optional[str] = None
    activity: Optional[str] = None
    years_smoked: Optional[int] = 0
    cigarettes_per_day: Optional[int] = 0
    target_quit_date: Optional[Any] = None
    reason_quitting: Optional[str] = None
    triggers: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    phone: Optional[str] = None
    activity: Optional[str] = None
    years_smoked: Optional[int] = None
    cigarettes_per_day: Optional[int] = None
    target_quit_date: Optional[Any] = None
    reason_quitting: Optional[str] = None
    triggers: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True
