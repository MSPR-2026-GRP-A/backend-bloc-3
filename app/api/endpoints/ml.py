from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.services.ml_service import train_model, predict_emission

router = APIRouter(prefix="/ml", tags=["Machine Learning"])


@router.post("/train", summary="Entraîne le modèle de prédiction Co2")
def train(session: Session = Depends(get_session)):
    try:
        return train_model(session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/predict", summary="Prédit l'émission Co2 d'un trip")
def predict(
    distance: int,
    duration: int,
    agency_name: str,
):
    return {
        "distance_km": distance,
        "duration_min": duration,
        "agency": agency_name,
        "predicted_co2_kg": predict_emission(distance, duration, agency_name),
    }