from fastapi import FastAPI

from app.api.routes import router


#************************
#* Configuration API    *
#************************

app = FastAPI(
    title="Futurisys ML API",
    description="API de deployment d'un modele de machine learning pour predire l'attrition collaborateur.",
    version="0.2.0",
)


#************************
#* Routes generales     *
#************************

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Futurisys ML"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


#************************
#* Enregistrement route *
#************************

app.include_router(router)
