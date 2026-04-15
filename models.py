from sqlalchemy import Column, Integer, String, Date, Boolean, Text
from database import Base



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    age = Column(Integer, nullable=True)
    phone = Column(String, nullable=True)
    activity = Column(String, nullable=True)
    years_smoked = Column(Integer, default=0)
    cigarettes_per_day = Column(Integer, default=0)
    target_quit_date = Column(Date, nullable=True)
    reason_quitting = Column(String, nullable=True)
    triggers = Column(String, nullable=True)


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  
    user_name = Column(String, nullable=True)  
    doctor_name = Column(String)
    appointment_date = Column(Date)
    appointment_time = Column(String)
    status = Column(String, default="Pending")  
    notes = Column(String, nullable=True)


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    subject = Column(String)
    message = Column(String)
    reply_message = Column(Text, nullable=True)
    is_replied = Column(Boolean, default=False)


class HabitDefinition(Base):
    __tablename__ = "habit_definitions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    name = Column(String)
    created_at = Column(Date)


class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    habit_definition_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)
    completed = Column(Boolean, default=False)
    date = Column(Date)


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    entry = Column(String)
    date = Column(Date)


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    license_number = Column(String)
    specialization = Column(String, nullable=True)
    profile_image = Column(String, nullable=True)
    is_approved = Column(Boolean, default=False)
