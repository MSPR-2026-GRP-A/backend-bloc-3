from typing import List, Optional
from pydantic import BaseModel, Field

class TripStep(BaseModel):
    "Un tronçon du trajet (un seul train)."
    trip_id: int
    trip_name: str
    origin: str
    destination: str
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None
    duration_minutes: Optional[int] = None
    distance_km: Optional[int] = None
    co2_kg: float = Field(..., description="Émission Co2 en kg (estimée si null en DB)")
    co2_estimated: bool = Field(
        False,
        description="True = Co2 estimée, False = data issue de la DB"
    )
    agency_name: Optional[str] = None

class RouteResponse(BaseModel):
    "Réponse complète d'un itinéraire calculé."
    origin: str
    destination: str
    steps: List[TripStep]
    total_co2_kg: float = Field(..., description="Co2 total cumulé en kg")
    total_duration_minutes: Optional[int] = None
    total_distance_km: Optional[int] = None
    nb_changes: int = Field(..., description="Nombre de correspondances (0 = direct)")
    has_estimated_co2: bool = Field(
        False,
        description="True si au moins un tronçon a une émission estimée"
    )

class RouteCompareResponse(BaseModel):
    "Comparaison entre l'itinéraire le plus vert et le plus rapide."
    co2_optimal: RouteResponse
    time_optimal: RouteResponse
    co2_saved_kg: float = Field(
        ...,
        description="Co2 économisé en choisissant l'itinéraire vert vs rapide"
    )
    time_lost_minutes: Optional[int] = Field(
        None,
        description="Minutes supplémentaires du trajet vert vs rapide (peut être négatif)"
    )