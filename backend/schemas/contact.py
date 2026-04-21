from pydantic import BaseModel, EmailStr
from typing import Optional


class ContactCreate(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str


class ContactResponse(ContactCreate):
    id: int
    reply_message: Optional[str] = None
    is_replied: bool = False

    class Config:
        from_attributes = True


class ContactReply(BaseModel):
    reply_message: str
