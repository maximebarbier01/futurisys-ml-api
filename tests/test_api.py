from copy import deepcopy
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.api import routes
from app.db.models import Employee, PredictionInputLog, PredictionOutputLog
from app.main import app

#***********************
#* Constantes et setup *
#***********************

# Client de test permettant d'appeler l'API sans lancer uvicorn
client = TestClient(app)

DATA_DIR = Path(__file__).parent / "data"

#*************************
#* Fonctions utilitaires *
#*************************

def load_json_fixture(filename: str) -> dict:
    return json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))


VALID_PAYLOADS = load_json_fixture("sample_valid_payloads.json")
INVALID_PAYLOADS = load_json_fixture("sample_invalid_payloads.json")
FUNCTIONAL_CASES = load_json_fixture("sample_functional_cases.json")


def get_valid_payload(name: str = "default_payload") -> dict:
    """Retourne un payload valide pour tester l'endpoint /predict."""
    return deepcopy(VALID_PAYLOADS[name])

def get_invalid_payload(name: str) -> dict:
    """Retourne un payload invalide pour tester l'endpoint /predict."""
    return deepcopy(INVALID_PAYLOADS[name])

def get_functional_case(name: str) -> dict:
    """Retourne un payload avec des cas fonctionnels pour tester l'endpoint /predict."""
    return deepcopy(FUNCTIONAL_CASES[name])

#******************************
#* Tests des routes generales *
#******************************

def test_root():
    """Teste que la route d'accueil répond correctement."""
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenue sur l'API Futurisys ML"}


def test_health():
    """Teste que la route de health check indique que l'API est disponible."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_schema():
    """Teste que le schéma OpenAPI est bien généré avec les routes principales."""
    response = client.get("/openapi.json")

    assert response.status_code == 200
    data = response.json()

    # Vérifie la structure générale du schéma OpenAPI
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data

    # Vérifie les métadonnées et les routes exposées par l'API
    assert data["info"]["title"] == "Futurisys ML API"
    assert "/" in data["paths"]
    assert "/health" in data["paths"]
    assert "/predict" in data["paths"]

#********************************
#* Tests fonctionnels /predict  *
#********************************

def test_predict_success():
    """Teste qu'une prédiction réussit avec un payload valide."""
    response = client.post("/predict", json=get_valid_payload())

    assert response.status_code == 200
    data = response.json()

    assert set(data.keys()) == {"prediction", "probability", "threshold", "label"}
    assert data["prediction"] in [0, 1]
    assert 0 <= data["probability"] <= 1
    assert 0 <= data["threshold"] <= 1
    assert data["label"] in ["attrition", "non_attrition"]


@pytest.mark.parametrize("case_name", ["stable_profile", "at_risk_profile"])
def test_predict_functional_cases(case_name):
    case = get_functional_case(case_name)

    response = client.post("/predict", json=case["payload"])

    assert response.status_code == 200
    data = response.json()

    assert data["prediction"] == case["expected_prediction"]
    assert data["label"] == case["expected_label"]
    assert 0 <= data["probability"] <= 1
    assert 0 <= data["threshold"] <= 1


def test_predict_logs_request_and_response(db_session):
    """Teste que l'appel à /predict enregistre bien les logs d'entrée et de sortie."""
    # Création d'un employé en base de test
    employee = Employee(**get_valid_payload())
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)

    # Ajout de l'id de l'employé dans le payload de prédiction
    payload = get_valid_payload()
    payload["employee_id"] = employee.id

    response = client.post("/predict", json=payload)

    assert response.status_code == 200

    # Récupération des logs créés en base
    input_log = db_session.query(PredictionInputLog).one()
    output_log = db_session.query(PredictionOutputLog).one()

    # Vérifie que les logs sont bien reliés à l'employé et entre eux
    assert input_log.employee_id == employee.id
    assert output_log.prediction_input_id == input_log.id

    # Vérifie la cohérence des valeurs loggées
    assert output_log.prediction in [0, 1]
    assert 0 <= output_log.probability <= 1
    assert output_log.label in ["attrition", "non_attrition"]

def test_predict_without_matching_employee_still_succeeds(db_session):
    payload = get_functional_case("at_risk_profile")["payload"]

    response = client.post("/predict", json=payload)

    assert response.status_code == 200

    input_log = db_session.query(PredictionInputLog).one()
    output_log = db_session.query(PredictionOutputLog).one()

    assert input_log.employee_id is None
    assert output_log.prediction_input_id == input_log.id


def test_predict_unknown_employee_id_returns_404():
    """Teste qu'un employee_id inexistant retourne une erreur 404."""
    response = client.post("/predict", json=get_invalid_payload("unknown_employee_id"))

    assert response.status_code == 404
    assert response.json() == {"detail": "Employee 999999 not found"}


def test_predict_success_without_database_tracking(monkeypatch, db_session):
    """Teste que la prédiction fonctionne même si le tracking en base échoue."""
    def raise_db_error(*args, **kwargs):
        raise SQLAlchemyError("database unavailable")

    monkeypatch.setattr(routes, "find_matching_employee", raise_db_error)

    response = client.post("/predict", json=get_valid_payload())

    assert response.status_code == 200
    assert db_session.query(PredictionInputLog).count() == 0
    assert db_session.query(PredictionOutputLog).count() == 0

#***********************************
#* Tests de validation /predict    *
#***********************************

def test_predict_missing_field():
    """Teste qu'un champ obligatoire manquant retourne une erreur 422."""
    payload = get_valid_payload()
    payload.pop("age")

    response = client.post("/predict", json=payload)

    assert response.status_code == 422


def test_predict_invalid_type():
    """Teste qu'un type invalide retourne une erreur 422."""
    response = client.post("/predict", json=get_invalid_payload("invalid_type_age"))

    assert response.status_code == 422



def test_predict_out_of_range_value():
    """Teste qu'une valeur hors intervalle autorisé retourne une erreur 422."""
    response = client.post(
        "/predict",
        json=get_invalid_payload("out_of_range_satisfaction"),
    )

    assert response.status_code == 422


def test_predict_invalid_category():
    """Teste qu'une catégorie non autorisée retourne une erreur 422."""
    response = client.post(
        "/predict",
        json=get_invalid_payload("invalid_category_gender"),
    )

    assert response.status_code == 422


def test_predict_invalid_percentage():
    """Teste qu'un pourcentage invalide retourne une erreur 422."""
    response = client.post("/predict", json=get_invalid_payload("invalid_percentage"))

    assert response.status_code == 422
