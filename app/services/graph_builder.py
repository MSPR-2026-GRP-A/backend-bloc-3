import networkx as nx
from sqlmodel import Session, select
from app.models.database_models import Trip, Agency  # adapte selon tes imports

# Facteur d'émission pour le train (kgCo2 par km)
ADEME_TRAIN_KG_PER_KM = 0.00369


def _estimate_co2(distance_km: int | None) -> float:
    "Estime le Co2 en kg si l'émission est absente en base."
    if not distance_km:
        return 0.0  # pas de distance = pas d'estimation possible
    return round(distance_km * ADEME_TRAIN_KG_PER_KM, 4)

def build_graph(session: Session) -> nx.DiGraph:
    """
    Construit un DiGraph NetworkX depuis la table trip.

    Chaque nœud = nom d'une gare (str)
    Chaque arc = un trip direct, avec comme poids :
        - weight_co2      → émission CO₂ réelle ou estimée (kg)
        - weight_duration → durée en minutes
        - trip_id, trip_name, agency_name, etc. (métadonnées)
    """
    G = nx.DiGraph()

    # Jointure trip + agency pour récup name agency
    statement = (
        select(Trip, Agency)
        .join(Agency, Trip.id_agency == Agency.id_agency)
    )
    results = session.exec(statement).all()

    for trip, agency in results:
        #DB en priorité, estimation sinon estimation
        co2_is_estimated = trip.emission is None
        co2_value = (
            float(trip.emission)
            if not co2_is_estimated
            else _estimate_co2(trip.distance)
        )

        # Ajout de l'arc origin => destination
        G.add_edge(
            trip.origin,
            trip.destination,
            # Poids utilisés par Dijkstra
            weight_co2=co2_value,
            weight_duration=trip.duration or 0,
            # Métadonnées pour construire la réponse API
            trip_id=trip.id_trip,
            trip_name=trip.name,
            departure_time=str(trip.departure_time) if trip.departure_time else None,
            arrival_time=str(trip.arrival_time) if trip.arrival_time else None,
            distance_km=trip.distance,
            co2_kg=co2_value,
            co2_estimated=co2_is_estimated,
            agency_name=agency.name,
        )

    return G