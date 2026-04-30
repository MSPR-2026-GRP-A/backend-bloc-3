import os
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

# Importer les modèles pour créer les tables
from app.models.models import (
    Agency, Route, Calendar, Stop, Trip, TripStop, CalendarDate
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)

# Créer toutes les tables
SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session