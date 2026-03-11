from pydantic import BaseModel
from datetime import date
from typing import Optional


class HabitCreate(BaseModel):
    name: str


class HabitUpdate(BaseModel):
    completed: bool
    date: date


class HabitResponse(BaseModel):
    id: int  # This will be the HabitDefinition ID
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
