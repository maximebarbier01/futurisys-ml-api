from sqlalchemy.orm import Session

from app.db.models import PredictionInputLog, PredictionOutputLog


def create_prediction_input(db: Session, input_data: dict) -> PredictionInputLog:
    prediction_input = PredictionInputLog(**input_data)
    db.add(prediction_input)
    db.commit()
    db.refresh(prediction_input)
    return prediction_input


def create_prediction_output(
    db: Session,
    prediction_input_id: int,
    prediction_result: dict,
    model_name: str | None = None,
    model_version: str | None = None,
) -> PredictionOutputLog:
    prediction_output = PredictionOutputLog(
        prediction_input_id=prediction_input_id,
        prediction=prediction_result["prediction"],
        probability=prediction_result["probability"],
        threshold=prediction_result["threshold"],
        label=prediction_result["label"],
        model_name=model_name,
        model_version=model_version,
    )
    db.add(prediction_output)
    db.commit()
    db.refresh(prediction_output)
    return prediction_output