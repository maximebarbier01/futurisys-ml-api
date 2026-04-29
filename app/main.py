from fastapi import FastAPI

from app.services.model_service import model_service

app = FastAPI(
    title="Futurisys ML API",
    description="API de déploiement d’un modèle de machine learning",
    version="0.1.0",
)


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Futurisys ML"}


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/predict")
def predict(input_data: dict):
    return model_service.predict(input_data)