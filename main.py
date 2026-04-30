from fastapi import FastAPI
from app.api.endpoints import hello

app = FastAPI(title="Mon API ML & Graph")

# On inclut notre router "Hello"
app.include_router(hello.router, prefix="/api/v1", tags=["Greeting"])

@app.get("/")
def root():
    return {"status": "L'API est en ligne"}