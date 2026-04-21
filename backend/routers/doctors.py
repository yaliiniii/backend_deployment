from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, database
from schemas import doctor as doctor_schemas
from typing import List
from security import get_password_hash, verify_password


router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("/", response_model=List[doctor_schemas.DoctorResponse])
def get_all_doctors(db: Session = Depends(database.get_db)):
    return db.query(models.Doctor).filter(models.Doctor.is_approved == True).all()


@router.post("/signup", response_model=doctor_schemas.DoctorResponse)
def signup(doctor: doctor_schemas.DoctorCreate, db: Session = Depends(database.get_db)):
    doctor.email = doctor.email.lower().strip()
    db_doctor = (
        db.query(models.Doctor).filter(models.Doctor.email == doctor.email).first()
    )
    if db_doctor:
        raise HTTPException(status_code=400, detail="Email already registered")

    doctor_data = doctor.model_dump()
    doctor_data["password"] = get_password_hash(doctor_data["password"])
    new_doctor = models.Doctor(**doctor_data)

    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    return new_doctor


@router.post("/login")
def login(doctor: doctor_schemas.DoctorLogin, db: Session = Depends(database.get_db)):
    email = doctor.email.lower().strip()
    db_doctor = db.query(models.Doctor).filter(models.Doctor.email == email).first()
    if not db_doctor or not verify_password(doctor.password, db_doctor.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    return {"id": db_doctor.id, "name": db_doctor.name, "email": db_doctor.email}


@router.get("/me", response_model=doctor_schemas.DoctorResponse)
def get_me(db: Session = Depends(database.get_db)):

    doctor = db.query(models.Doctor).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


@router.put("/me", response_model=doctor_schemas.DoctorResponse)
def update_me(
    doctor_update: doctor_schemas.DoctorCreate, db: Session = Depends(database.get_db)
):
    db_doctor = db.query(models.Doctor).first()
    if not db_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    update_data = doctor_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_doctor, key, value)

    db.commit()
    db.refresh(db_doctor)
    return db_doctor


@router.delete("/me")
def delete_me(db: Session = Depends(database.get_db)):
    db_doctor = db.query(models.Doctor).first()
    if not db_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    db.delete(db_doctor)
    db.commit()
    return {"message": "Doctor deleted"}
