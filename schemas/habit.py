from pydantic import BaseModel
from datetime import date


class HabitCreate(BaseModel):
    name: str


class HabitUpdate(BaseModel):
    completed: bool
    date: date


class HabitResponse(BaseModel):
    id: int  
    name: str
    completed: bool = False
    date: date

    class Config:
        from_attributes = True


class JournalEntryCreate(BaseModel):
    entry: str
    date: date


class JournalEntryResponse(JournalEntryCreate):
    id: int

    class Config:
        from_attributes = True
