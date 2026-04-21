from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date as date_obj, timedelta
import models, database
from schemas import habit as habit_schemas
from typing import List

router = APIRouter(prefix="/habits", tags=["habits & journal"])


# =========================
# GET ALL HABITS (calendar view)
# =========================
@router.get("/all", response_model=List[habit_schemas.HabitResponse])
def get_all_habits(user_id: int, db: Session = Depends(database.get_db)):

    definitions = db.query(models.HabitDefinition).filter(
        models.HabitDefinition.user_id == user_id
    ).all()

    completions = db.query(models.Habit).filter(
        models.Habit.user_id == user_id
    ).all()

    # Helper to ensure we have a date object (not datetime)
    def to_date(d):
        return d.date() if hasattr(d, 'date') else d

    # Get all relevant dates (from earliest track or 7 days ago, until today)
    all_dates_set = {date_obj.today(), date_obj.today() - timedelta(days=6)}
    for c in completions:
        if c.date:
            all_dates_set.add(to_date(c.date))
    
    first_date = min(all_dates_set)
    today = date_obj.today()
    
    # Generate all dates in the range
    all_dates = []
    curr = first_date
    while curr <= today:
        all_dates.append(curr)
        curr += timedelta(days=1)

    results = []

    for d in all_dates:
        # Pre-filter completions for this date to speed up
        completion_map = {
            c.habit_definition_id: c.completed
            for c in completions
            if to_date(c.date) == d
        }

        for definition in definitions:
            # Show all habits for all dates in the range
            results.append({
                "id": definition.id,
                "name": definition.name,
                "completed": completion_map.get(definition.id, False),
                "date": d
            })

    return results


# =========================
# GET HABITS FOR ONE DATE
# =========================
@router.get("/", response_model=List[habit_schemas.HabitResponse])
def get_habits(user_id: int, date: date_obj, db: Session = Depends(database.get_db)):

    definitions = db.query(models.HabitDefinition).filter(
        models.HabitDefinition.user_id == user_id
    ).all()

    completions = db.query(models.Habit).filter(
        models.Habit.user_id == user_id,
        models.Habit.date == date
    ).all()

    completion_map = {
        c.habit_definition_id: c.completed
        for c in completions
    }

    return [
        {
            "id": d.id,
            "name": d.name,
            "completed": completion_map.get(d.id, False),
            "date": date
        }
        for d in definitions
    ]


# =========================
# CREATE HABIT (ONLY definition table)
# =========================
@router.post("/", response_model=habit_schemas.HabitResponse)
def create_habit(
    habit: habit_schemas.HabitCreate,
    user_id: int,
    db: Session = Depends(database.get_db),
):
    # Use provided created_at if available and valid
    creation_date = habit.created_at if habit.created_at else date_obj.today()

    db_definition = models.HabitDefinition(
        name=habit.name,
        user_id=user_id,
        created_at=creation_date
    )

    db.add(db_definition)
    db.commit()
    db.refresh(db_definition)

    return {
        "id": db_definition.id,
        "name": db_definition.name,
        "completed": False,
        "date": creation_date
    }


# =========================
# UPDATE COMPLETION STATUS
# =========================
@router.put("/{habit_id}", response_model=habit_schemas.HabitResponse)
def update_habit_status(
    habit_id: int,
    habit_update: habit_schemas.HabitUpdate,
    db: Session = Depends(database.get_db),
):

    definition = db.query(models.HabitDefinition).filter(
        models.HabitDefinition.id == habit_id
    ).first()

    if not definition:
        raise HTTPException(status_code=404, detail="Habit not found")

    db_habit = db.query(models.Habit).filter(
        models.Habit.habit_definition_id == habit_id,
        models.Habit.date == habit_update.date
    ).first()

    if db_habit:
        db_habit.completed = habit_update.completed
    else:
        db_habit = models.Habit(
            habit_definition_id=habit_id,
            user_id=definition.user_id,
            completed=habit_update.completed,
            date=habit_update.date
        )
        db.add(db_habit)

    db.commit()
    db.refresh(db_habit)

    return {
        "id": definition.id,
        "name": definition.name,
        "completed": db_habit.completed,
        "date": db_habit.date
    }


# =========================
# DELETE HABIT
# =========================
@router.delete("/{habit_id}")
def delete_habit(habit_id: int, db: Session = Depends(database.get_db)):

    definition = db.query(models.HabitDefinition).filter(
        models.HabitDefinition.id == habit_id
    ).first()

    if not definition:
        raise HTTPException(status_code=404, detail="Habit not found")

    db.query(models.Habit).filter(
        models.Habit.habit_definition_id == habit_id
    ).delete()

    db.delete(definition)
    db.commit()

    return {"message": "Habit deleted"}


# =========================
# JOURNAL
# =========================
@router.get("/journal", response_model=List[habit_schemas.JournalEntryResponse])
def get_journal_entries(
    user_id: int = None,
    date: date_obj = None,
    db: Session = Depends(database.get_db)
):

    query = db.query(models.JournalEntry)

    if user_id:
        query = query.filter(models.JournalEntry.user_id == user_id)

    if date:
        query = query.filter(models.JournalEntry.date == date)

    return query.all()


@router.post("/journal", response_model=habit_schemas.JournalEntryResponse)
def create_journal_entry(
    entry: habit_schemas.JournalEntryCreate,
    user_id: int = None,
    db: Session = Depends(database.get_db),
):

    query = db.query(models.JournalEntry).filter(
        models.JournalEntry.date == entry.date
    )

    if user_id:
        query = query.filter(models.JournalEntry.user_id == user_id)
    else:
        query = query.filter(models.JournalEntry.user_id.is_(None))

    existing = query.first()

    if existing:
        raise HTTPException(status_code=400, detail="Journal already exists")

    db_entry = models.JournalEntry(**entry.model_dump())

    if user_id:
        db_entry.user_id = user_id

    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)

    return db_entry


@router.put("/journal/{entry_id}", response_model=habit_schemas.JournalEntryResponse)
def update_journal_entry(
    entry_id: int,
    entry_update: habit_schemas.JournalEntryCreate,
    db: Session = Depends(database.get_db),
):

    db_entry = db.query(models.JournalEntry).filter(
        models.JournalEntry.id == entry_id
    ).first()

    if not db_entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    for key, value in entry_update.model_dump().items():
        setattr(db_entry, key, value)

    db.commit()
    db.refresh(db_entry)

    return db_entry


@router.delete("/journal/{entry_id}")
def delete_journal_entry(entry_id: int, db: Session = Depends(database.get_db)):

    db_entry = db.query(models.JournalEntry).filter(
        models.JournalEntry.id == entry_id
    ).first()

    if not db_entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    db.delete(db_entry)
    db.commit()

    return {"message": "Entry deleted"}