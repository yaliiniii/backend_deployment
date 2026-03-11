from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, database
from schemas import user as user_schemas
from datetime import datetime
from .admin import ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_TOKEN


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup", response_model=user_schemas.UserResponse)
def signup(user: user_schemas.UserCreate, db: Session = Depends(database.get_db)):
    user.email = user.email.lower().strip()
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    target_date = None
    if user.target_quit_date:
        try:
            target_date = datetime.strptime(user.target_quit_date, "%Y-%m-%d").date()
        except ValueError:
            pass

    new_user = models.User(
        name=user.name,
        email=user.email,
        password=user.password,
        age=user.age,
        phone=user.phone,
        activity=user.activity,
        years_smoked=user.years_smoked,
        cigarettes_per_day=user.cigarettes_per_day,
        target_quit_date=target_date,
        reason_quitting=user.reason_quitting,
        triggers=user.triggers,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login")
def login(user: user_schemas.UserLogin, db: Session = Depends(database.get_db)):
    email = user.email.lower().strip()
    
    # Check for Admin Credentials first
    if email == ADMIN_EMAIL and user.password == ADMIN_PASSWORD:
        return {
            "id": 0, 
            "name": "Administrator", 
            "email": ADMIN_EMAIL, 
            "role": "admin", 
            "token": ADMIN_TOKEN
        }
        
    db_user = db.query(models.User).filter(models.User.email == email).first()
    if not db_user or db_user.password != user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    return {"id": db_user.id, "name": db_user.name, "email": db_user.email, "role": "user"}


@router.get("/me", response_model=user_schemas.UserResponse)
def get_me(db: Session = Depends(database.get_db)):
    # Placeholder for current user logic
    user = db.query(models.User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/me", response_model=user_schemas.UserResponse)
def update_me(
    user_update: user_schemas.UserUpdate, db: Session = Depends(database.get_db)
):
    db_user = db.query(models.User).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True)

    # Check if email is being updated and if it's already taken by another user
    if "email" in update_data and update_data["email"] != db_user.email:
        existing_user = (
            db.query(models.User)
            .filter(models.User.email == update_data["email"])
            .first()
        )
        if existing_user:
            raise HTTPException(
                status_code=400, detail="Email already taken by another user"
            )

    if "target_quit_date" in update_data and update_data["target_quit_date"]:
        try:
            if isinstance(update_data["target_quit_date"], str):
                update_data["target_quit_date"] = datetime.strptime(
                    update_data["target_quit_date"], "%Y-%m-%d"
                ).date()
        except ValueError:
            del update_data["target_quit_date"]

    for key, value in update_data.items():
        setattr(db_user, key, value)

    try:
        db.commit()
        db.refresh(db_user)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database update failed")
    return db_user


@router.delete("/me")
def delete_me(db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted"}


@router.get("/{user_id}", response_model=user_schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/{user_id}", response_model=user_schemas.UserResponse)
def update_user(
    user_id: int,
    user_update: user_schemas.UserUpdate,
    db: Session = Depends(database.get_db),
):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True)

    # Check if email is being updated and if it's already taken by another user
    if "email" in update_data and update_data["email"] != db_user.email:
        existing_user = (
            db.query(models.User)
            .filter(models.User.email == update_data["email"])
            .first()
        )
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already taken")

    if "target_quit_date" in update_data and update_data["target_quit_date"]:
        try:
            if isinstance(update_data["target_quit_date"], str):
                update_data["target_quit_date"] = datetime.strptime(
                    update_data["target_quit_date"], "%Y-%m-%d"
                ).date()
        except ValueError:
            del update_data["target_quit_date"]

    for key, value in update_data.items():
        setattr(db_user, key, value)

    try:
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database update failed")
    return db_user


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted"}
