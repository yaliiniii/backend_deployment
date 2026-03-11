from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, database
from schemas import contact as contact_schemas

from typing import List

router = APIRouter(prefix="/contact", tags=["contact"])


@router.post("/", response_model=contact_schemas.ContactResponse)
def create_contact(
    contact: contact_schemas.ContactCreate, db: Session = Depends(database.get_db)
):
    db_contact = models.Contact(**contact.model_dump())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


@router.get("/{email}", response_model=List[contact_schemas.ContactResponse])
def get_user_messages(email: str, db: Session = Depends(database.get_db)):
    """Get all messages and replies for a specific user email."""
    messages = (
        db.query(models.Contact)
        .filter(models.Contact.email == email)
        .order_by(models.Contact.id.desc())
        .all()
    )
    return messages
