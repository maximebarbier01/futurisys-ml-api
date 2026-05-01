from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="Futurisys ML API",
    description="API de déploiement d’un modèle de machine learning pour prédire l’attrition collaborateur.",
    version="0.2.0",
)


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Futurisys ML"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(router)