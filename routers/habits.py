from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
import models, database
from schemas import habit as habit_schemas
from typing import List

router = APIRouter(prefix="/habits", tags=["habits & journal"])


# All habits across all dates (for the progress page)
@router.get("/all", response_model=List[habit_schemas.HabitResponse])
def get_all_habits(
    user_id: int,
    db: Session = Depends(database.get_db)
):
    definitions = db.query(models.HabitDefinition).filter(models.HabitDefinition.user_id == user_id).all()
    definition_map = {d.id: d.name for d in definitions}

    completions = db.query(models.Habit).filter(models.Habit.user_id == user_id).all()

    results = []
    for c in completions:
        name = definition_map.get(c.habit_definition_id, "Unknown")
        results.append({
            "id": c.habit_definition_id,
            "name": name,
            "completed": c.completed,
            "date": c.date
        })
    return results


# Habits
@router.get("/", response_model=List[habit_schemas.HabitResponse])
def get_habits(
    user_id: int,
    date: date,
    db: Session = Depends(database.get_db)
):
    # Fetch all habit definitions for the user
    definitions = db.query(models.HabitDefinition).filter(models.HabitDefinition.user_id == user_id).all()
    
    # Fetch completion records for this specific date
    completions = db.query(models.Habit).filter(
        models.Habit.user_id == user_id,
        models.Habit.date == date
    ).all()
    
    # Map completion records to definition IDs
    completion_map = {c.habit_definition_id: c.completed for c in completions}
    
    # Combine definition with completion record
    results = []
    for definition in definitions:
        results.append({
            "id": definition.id,
            "name": definition.name,
            "completed": completion_map.get(definition.id, False),
            "date": date
        })
        
    return results


@router.post("/", response_model=habit_schemas.HabitResponse)
def create_habit(
    habit: habit_schemas.HabitCreate,
    user_id: int,
    db: Session = Depends(database.get_db),
):
    from datetime import date as date_obj
    db_definition = models.HabitDefinition(
        name=habit.name,
        user_id=user_id,
        created_at=date_obj.today()
    )
    db.add(db_definition)
    db.commit()
    db.refresh(db_definition)
    
    return {
        "id": db_definition.id,
        "name": db_definition.name,
        "completed": False,
        "date": date_obj.today()
    }


@router.put("/{habit_id}", response_model=habit_schemas.HabitResponse)
def update_habit_status(
    habit_id: int,  # This is the HabitDefinition ID
    habit_update: habit_schemas.HabitUpdate,
    db: Session = Depends(database.get_db),
):
    # Check if a completion record already exists for this date and habit definition
    db_habit = db.query(models.Habit).filter(
        models.Habit.habit_definition_id == habit_id,
        models.Habit.date == habit_update.date
    ).first()
    
    definition = db.query(models.HabitDefinition).filter(models.HabitDefinition.id == habit_id).first()
    if not definition:
        raise HTTPException(status_code=404, detail="Habit not found")

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


@router.delete("/{habit_id}")
def delete_habit(habit_id: int, db: Session = Depends(database.get_db)):
    # This deletes the definition and all associated history
    db_definition = db.query(models.HabitDefinition).filter(models.HabitDefinition.id == habit_id).first()
    if not db_definition:
        raise HTTPException(status_code=404, detail="Habit not found")
        
    # Delete all daily records first
    db.query(models.Habit).filter(models.Habit.habit_definition_id == habit_id).delete()
    
    # Delete the definition
    db.delete(db_definition)
    db.commit()
    return {"message": "Habit deleted"}


# Journal
@router.get("/journal", response_model=List[habit_schemas.JournalEntryResponse])
def get_journal_entries(
    user_id: int = None,
    date: date = None,
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
    # Check if an entry already exists for this user and date
    query = db.query(models.JournalEntry).filter(models.JournalEntry.date == entry.date)
    if user_id:
        query = query.filter(models.JournalEntry.user_id == user_id)
    else:
        query = query.filter(models.JournalEntry.user_id.is_(None))
        
    existing_entry = query.first()
    
    if existing_entry:
        raise HTTPException(
            status_code=400, detail="Journal entry already exists for this day"
        )

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
    db_entry = (
        db.query(models.JournalEntry).filter(models.JournalEntry.id == entry_id).first()
    )
    if not db_entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    update_data = entry_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_entry, key, value)

    db.commit()
    db.refresh(db_entry)
    return db_entry


@router.delete("/journal/{entry_id}")
def delete_journal_entry(entry_id: int, db: Session = Depends(database.get_db)):
    db_entry = (
        db.query(models.JournalEntry).filter(models.JournalEntry.id == entry_id).first()
    )
    if not db_entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(db_entry)
    db.commit()
    return {"message": "Entry deleted"}
