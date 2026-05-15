import logging

from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.repository import (
    create_prediction_input,
    create_prediction_output,
    find_matching_employee,
)
from app.schemas.prediction import PredictionInput, PredictionOutput
from app.services.model_service import model_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/predict", response_model=PredictionOutput)
def predict(input_data: PredictionInput, db: Session = Depends(get_db)):
    payload = input_data.model_dump()
    prediction_result = model_service.predict(payload)

    try:
        employee = find_matching_employee(db, payload)
        prediction_input = create_prediction_input(
            db,
            payload,
            employee_id=employee.id if employee else None,
        )
        create_prediction_output(
            db=db,
            prediction_input_id=prediction_input.id,
            prediction_result=prediction_result,
            model_name=model_service.display_name,
            model_version=model_service.model_version,
        )
    except SQLAlchemyError as exc:
        db.rollback()
        logger.warning(
            "Prediction tracking unavailable; returning prediction without persistence: %s",
            exc,
        )

    return prediction_result
