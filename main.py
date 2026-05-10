from fastapi import FastAPI
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator
import joblib
import os

from app.api.endpoints import graph, ml, trips
from app.database import get_session
from app.services.graph_builder import build_graph
from app.services.graph_cache import GraphCache

ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Chargement du modèle ML
    model_path = "app/ml_assets/emission_model.joblib"
    if os.path.exists(model_path):
        print("Modèle ML chargé.")
    else:
        print("Aucun modèle ML trouvé utilisez POST /ap/ml/train pour l'entraîner.")

    # Construction du graphe NetworkX une seule fois
    session = next(get_session())
    try:
        G = build_graph(session)
        GraphCache.set(G)
    finally:
        session.close()

    yield

    ml_models.clear()
    GraphCache.invalidate()

app = FastAPI(
    title="OB Rail — CO₂ Optimizer",
    lifespan=lifespan,
)

# Prometheus expose /metrics
Instrumentator().instrument(app).expose(app)

app.include_router(trips.router, prefix="/api")
app.include_router(graph.router, prefix="/api")
app.include_router(ml.router, prefix="/api")

@app.get("/")
def root():
    return {"status": "L'API est en ligne"}