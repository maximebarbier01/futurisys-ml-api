from fastapi.testclient import TestClient

from app.main import app
from app.schemas.prediction import PREDICTION_INPUT_EXAMPLE

client = TestClient(app)


def get_valid_payload():
    return dict(PREDICTION_INPUT_EXAMPLE)


def test_predict_success():
    response = client.post("/predict", json=get_valid_payload())

    assert response.status_code == 200
    data = response.json()

    assert "prediction" in data
    assert "probability" in data
    assert 0 <= data["probability"] <= 1


def test_predict_missing_field():
    payload = get_valid_payload()
    payload.pop("age")

    response = client.post("/predict", json=payload)

    assert response.status_code == 422


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
