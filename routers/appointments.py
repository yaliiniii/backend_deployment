from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, database
from schemas import appointment as appointment_schemas
from typing import List

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("/", response_model=List[appointment_schemas.AppointmentResponse])
def get_all_appointments(db: Session = Depends(database.get_db)):
    return db.query(models.Appointment).all()


@router.post("/", response_model=appointment_schemas.AppointmentResponse)
def book_appointment(
    appointment: appointment_schemas.AppointmentCreate,
    db: Session = Depends(database.get_db),
):
    db_appointment = models.Appointment(**appointment.model_dump())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment


@router.get("/user/me", response_model=List[appointment_schemas.AppointmentResponse])
def get_user_appointments(db: Session = Depends(database.get_db)):
    
    return db.query(models.Appointment).all()


@router.get("/doctor/me", response_model=List[appointment_schemas.AppointmentResponse])
def get_doctor_appointments(db: Session = Depends(database.get_db)):
   
    return db.query(models.Appointment).all()


@router.put("/{app_id}", response_model=appointment_schemas.AppointmentResponse)
def update_appointment(
    app_id: int,
    appointment_update: appointment_schemas.AppointmentCreate,
    db: Session = Depends(database.get_db),
):
    db_app = (
        db.query(models.Appointment).filter(models.Appointment.id == app_id).first()
    )
    if not db_app:
        raise HTTPException(status_code=404, detail="Appointment not found")

    update_data = appointment_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_app, key, value)

    db.commit()
    db.refresh(db_app)
    return db_app


@router.delete("/{app_id}")
def delete_appointment(app_id: int, db: Session = Depends(database.get_db)):
    db_app = (
        db.query(models.Appointment).filter(models.Appointment.id == app_id).first()
    )
    if not db_app:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db.delete(db_app)
    db.commit()
    return {"message": "Appointment deleted"}


@router.patch(
    "/{app_id}/status", response_model=appointment_schemas.AppointmentResponse
)
def update_appointment_status(
    app_id: int,
    status: str,
    db: Session = Depends(database.get_db),
):
    db_app = (
        db.query(models.Appointment).filter(models.Appointment.id == app_id).first()
    )
    if not db_app:
        raise HTTPException(status_code=404, detail="Appointment not found")

    db_app.status = status
    db.commit()
    db.refresh(db_app)
    return db_app
