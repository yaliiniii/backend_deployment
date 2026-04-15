from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, database
from schemas import doctor as doctor_schemas
from schemas import contact as contact_schemas
from schemas import admin as admin_schemas
from typing import List
from fastapi.security import APIKeyHeader

router = APIRouter(prefix="/admin", tags=["admin"])


ADMIN_EMAIL = "admin@freshpath.com"
ADMIN_PASSWORD = "admin123"
ADMIN_TOKEN = "freshpath-admin-secret-token"

header_scheme = APIKeyHeader(name="Authorization")

def get_admin_user(token: str = Depends(header_scheme)):
    if token != f"Bearer {ADMIN_TOKEN}":
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Admin access required"
        )
    return ADMIN_EMAIL

@router.post("/login", response_model=admin_schemas.AdminResponse)
def admin_login(login_data: admin_schemas.AdminLogin):
    if login_data.email == ADMIN_EMAIL and login_data.password == ADMIN_PASSWORD:
        return {"email": ADMIN_EMAIL, "token": ADMIN_TOKEN}
    raise HTTPException(status_code=401, detail="Invalid admin credentials")


@router.get("/doctors", response_model=List[doctor_schemas.DoctorResponse])
def get_all_doctors(db: Session = Depends(database.get_db), admin: str = Depends(get_admin_user)):
    """Get all doctors (approved and pending) for admin review."""
    return db.query(models.Doctor).all()


@router.get("/doctors/pending", response_model=List[doctor_schemas.DoctorResponse])
def get_pending_doctors(db: Session = Depends(database.get_db), admin: str = Depends(get_admin_user)):
    """Get only pending (unapproved) doctors."""
    return db.query(models.Doctor).filter(models.Doctor.is_approved == False).all()


@router.put("/doctors/{doctor_id}/approve", response_model=doctor_schemas.DoctorResponse)
def approve_doctor(doctor_id: int, db: Session = Depends(database.get_db), admin: str = Depends(get_admin_user)):
    """Approve a doctor so they appear on the appointments page."""
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    doctor.is_approved = True
    db.commit()
    db.refresh(doctor)
    return doctor


@router.put("/doctors/{doctor_id}/reject")
def reject_doctor(doctor_id: int, db: Session = Depends(database.get_db), admin: str = Depends(get_admin_user)):
    """Reject (delete) a doctor application."""
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    db.delete(doctor)
    db.commit()
    return {"message": "Doctor application rejected and removed"}


@router.get("/contacts", response_model=List[contact_schemas.ContactResponse])
def get_all_contacts(db: Session = Depends(database.get_db), admin: str = Depends(get_admin_user)):
    """Get all contact messages for admin review."""
    return db.query(models.Contact).order_by(models.Contact.id.desc()).all()


@router.put("/contacts/{contact_id}/reply", response_model=contact_schemas.ContactResponse)
def reply_to_contact(
    contact_id: int,
    reply: contact_schemas.ContactReply,
    db: Session = Depends(database.get_db),
    admin: str = Depends(get_admin_user)
):
    """Save admin reply to a contact message."""
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if not db_contact:
        raise HTTPException(status_code=404, detail="Message not found")
    db_contact.reply_message = reply.reply_message
    db_contact.is_replied = True
    db.commit()
    db.refresh(db_contact)
    return db_contact
@router.delete("/contacts/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(database.get_db), admin: str = Depends(get_admin_user)):
    """Delete a contact message."""
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if not db_contact:
        raise HTTPException(status_code=404, detail="Message not found")
    db.delete(db_contact)
    db.commit()
    return {"message": "Message deleted successfully"}
