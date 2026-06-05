import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import require_api_key
from app.db.database import get_db
from app.db.repository import (
    create_prediction_input,
    create_prediction_output,
    find_matching_employee,
    get_employee_by_id,
)
from app.schemas.prediction import (
    PREDICTION_OUTPUT_EXAMPLE,
    PredictionInput,
    PredictionOutput,
)
from app.services.model_service import model_service


#************************
#* Router et logs       *
#************************

router = APIRouter(dependencies=[Depends(require_api_key)])
logger = logging.getLogger(__name__)


#************************
#* Endpoint prediction  *
#************************

@router.post(
    "/predict",
    response_model=PredictionOutput,
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": PREDICTION_OUTPUT_EXAMPLE,
                }
            }
        }
    },
)
def predict(input_data: PredictionInput, db: Session = Depends(get_db)):
    payload = input_data.model_dump(exclude_none=True)
    employee_id = payload.pop("employee_id", None)
    prediction_result = model_service.predict(payload)

    try:
        employee = None

        if employee_id is not None:
            employee = get_employee_by_id(db, employee_id)
            if employee is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Employee {employee_id} not found",
                )
        else:
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
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        logger.warning(
            "Prediction tracking unavailable; returning prediction without persistence: %s",
            exc,
        )

    return prediction_result
