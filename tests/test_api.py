from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.api import routes
from app.db.models import Employee, PredictionInputLog, PredictionOutputLog
from app.main import app
from app.schemas.prediction import PREDICTION_INPUT_EXAMPLE

client = TestClient(app)


def get_valid_payload():
    return dict(PREDICTION_INPUT_EXAMPLE)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenue sur l'API Futurisys ML"}


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_schema():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    data = response.json()

    assert "openapi" in data
    assert "info" in data
    assert "paths" in data
    assert data["info"]["title"] == "Futurisys ML API"
    assert "/" in data["paths"]
    assert "/health" in data["paths"]
    assert "/predict" in data["paths"]


def test_predict_success():
    response = client.post("/predict", json=get_valid_payload())

    assert response.status_code == 200
    data = response.json()

    assert set(data.keys()) == {"prediction", "probability", "threshold", "label"}
    assert data["prediction"] in [0, 1]
    assert 0 <= data["probability"] <= 1
    assert 0 <= data["threshold"] <= 1
    assert data["label"] in ["attrition", "non_attrition"]


def test_predict_logs_request_and_response(db_session):
    employee = Employee(**get_valid_payload())
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)

    payload = get_valid_payload()
    payload["employee_id"] = employee.id

    response = client.post("/predict", json=payload)

    assert response.status_code == 200

    input_log = db_session.query(PredictionInputLog).one()
    output_log = db_session.query(PredictionOutputLog).one()

    assert input_log.employee_id == employee.id
    assert output_log.prediction_input_id == input_log.id
    assert output_log.prediction in [0, 1]
    assert 0 <= output_log.probability <= 1
    assert output_log.label in ["attrition", "non_attrition"]


def test_predict_unknown_employee_id_returns_404():
    payload = get_valid_payload()
    payload["employee_id"] = 999999

    response = client.post("/predict", json=payload)

    assert response.status_code == 404
    assert response.json() == {"detail": "Employee 999999 not found"}


def test_predict_success_without_database_tracking(monkeypatch, db_session):
    def raise_db_error(*args, **kwargs):
        raise SQLAlchemyError("database unavailable")

    monkeypatch.setattr(routes, "find_matching_employee", raise_db_error)

    response = client.post("/predict", json=get_valid_payload())

    assert response.status_code == 200
    assert db_session.query(PredictionInputLog).count() == 0
    assert db_session.query(PredictionOutputLog).count() == 0


def test_predict_missing_field():
    payload = get_valid_payload()
    payload.pop("age")

    response = client.post("/predict", json=payload)

    assert response.status_code == 422


def test_predict_invalid_type():
    payload = get_valid_payload()
    payload["age"] = "trente-huit"

    response = client.post("/predict", json=payload)

    assert response.status_code == 422


def test_predict_out_of_range_value():
    payload = get_valid_payload()
    payload["satisfaction_employee_equipe"] = 7

    response = client.post("/predict", json=payload)

    assert response.status_code == 422


def test_predict_invalid_category():
    payload = get_valid_payload()
    payload["genre"] = "Homme"

    response = client.post("/predict", json=payload)

    assert response.status_code == 422


def test_predict_invalid_percentage():
    payload = get_valid_payload()
    payload["augementation_salaire_precedente"] = 1.5

    response = client.post("/predict", json=payload)

    assert response.status_code == 422
