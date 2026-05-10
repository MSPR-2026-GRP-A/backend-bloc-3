import os
import joblib
import numpy as np
from sqlmodel import Session, select
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

from app.models.database_models import Trip, Agency

MODEL_PATH = "app/services/emission_model.joblib"

def _load_training_data(session: Session) -> tuple:
    "Charge les trips avec emission connue depuis la DB. Retourne X (features) et y (cible emission)."
    statement = (
        select(Trip, Agency)
        .join(Agency, Trip.id_agency == Agency.id_agency)
        .where(Trip.emission.is_not(None))
        .where(Trip.distance.is_not(None))
        .where(Trip.duration.is_not(None))
    )
    results = session.exec(statement).all()

    if not results:
        raise ValueError("Aucune donnée d'entraînement disponible.")

    X, y = [], []
    for trip, agency in results:
        X.append([
            trip.distance,           # numérique
            trip.duration,           # numérique
            agency.name or "Unknown", # catégoriel
        ])
        y.append(float(trip.emission))

    return np.array(X, dtype=object), np.array(y, dtype=float)

def train_model(session: Session) -> dict:
    "Entraîne un modeèle Random Forest sur les trips avec emission connue. Sauvegarde le modèle dans services/ et retourne les métriques."
    X, y = _load_training_data(session)

    # Pipeline : encodage agency + Random Forest
    preprocessor = ColumnTransformer(transformers=[
        ("num", "passthrough", [0, 1]),        # distance, duration
        ("cat", OrdinalEncoder(
            handle_unknown="use_encoded_value",
            unknown_value=-1
        ), [2]),                                 # agency
    ])

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            n_jobs=-1,
        )),
    ])

    # Split train/test 80/20 (si assez de données)
    if len(X) >= 10:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        mae = round(mean_absolute_error(y_test, y_pred), 4)
        r2  = round(r2_score(y_test, y_pred), 4)
    else:
        # Trop peu de données → entraînement sur tout
        pipeline.fit(X, y)
        mae, r2 = None, None

    # Sauvegarde
    os.makedirs("app/services", exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"🤖 Modèle entraîné sur {len(X)} trips et sauvegardé.")

    return {
        "status": "trained",
        "samples": len(X),
        "mae_kg_co2": mae,
        "r2_score": r2,
    }


def predict_emission(distance: int, duration: int, agency_name: str) -> float:
    "Prédit l'émission CO₂ (kg) d'un trip via le modèle entraîné sinon utilise l'estimation ADEME si le modèle n'existe pas."
    if not os.path.exists(MODEL_PATH):
        # ADEME si pas encore de modèle
        return round((distance or 0) * 0.00369, 4)

    pipeline = joblib.load(MODEL_PATH)
    X = np.array([[distance, duration, agency_name]], dtype=object)
    prediction = pipeline.predict(X)[0]
    return round(float(prediction), 4)