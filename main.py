from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
import database
from routers import users, contact, appointments, habits, doctors, admin


models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="FreshPath API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)   
 

app.include_router(users.router, prefix="/api")
app.include_router(doctors.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(habits.router, prefix="/api")
app.include_router(appointments.router, prefix="/api")
app.include_router(contact.router, prefix="/api")
 

@app.get("/")
def read_root():
    return {"message": "Welcome to FreshPath API"}

 