from pydantic import BaseModel
from datetime import date
from typing import Optional


class AppointmentCreate(BaseModel):
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    doctor_name: str
    appointment_date: date
    appointment_time: str
    status: Optional[str] = "Pending"
    notes: Optional[str] = None


class AppointmentResponse(AppointmentCreate):
    id: int

    class Config:
        from_attributes = True
