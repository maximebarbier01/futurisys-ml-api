from fastapi import APIRouter

from app.schemas.prediction import PredictionInput, PredictionOutput
from app.services.model_service import model_service

router = APIRouter()


@router.post("/predict", response_model=PredictionOutput)
def predict(input_data: PredictionInput):
    return model_service.predict(input_data.model_dump())