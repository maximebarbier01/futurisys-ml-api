from copy import deepcopy
import json
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient # pour tester l'API sans lancer un serveur Uvicorn
from sqlalchemy.exc import SQLAlchemyError

from app.api import routes
from app.db.models import Employee, PredictionInputLog, PredictionOutputLog
from app.main import app


#********************************
#* Constantes et configuration  *
#********************************

# Client de test FastAPI.
client = TestClient(app)

# Ajoute automatiquement l'API key de test à toutes les requêtes du client.
client.headers.update({os.environ["API_KEY_HEADER_NAME"]: os.environ["API_KEY"]})

# Dossier contenant les payloads JSON utilisés par les tests.
DATA_DIR = Path(__file__).parent / "data"


#********************************
#* Fonctions utilitaires        *
#********************************

def load_json_fixture(filename: str) -> dict:
    """
    Charge un fichier JSON depuis tests/data.
    """
    return json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))

# Chargement des jeux de données de test.
VALID_PAYLOADS = load_json_fixture("sample_valid_payloads.json")
INVALID_PAYLOADS = load_json_fixture("sample_invalid_payloads.json")
FUNCTIONAL_CASES = load_json_fixture("sample_functional_cases.json")


def get_valid_payload(name: str = "default_payload") -> dict:
    """
    Retourne une copie indépendante d'un payload valide.
    """
    return deepcopy(VALID_PAYLOADS[name])


def get_invalid_payload(name: str) -> dict:
    """
    Retourne une copie indépendante d'un payload invalide.
    """
    return deepcopy(INVALID_PAYLOADS[name])


def get_functional_case(name: str) -> dict:
    """
    Retourne une copie indépendante d'un cas fonctionnel.
    """
    return deepcopy(FUNCTIONAL_CASES[name])


#********************************
#* Tests routes generales       *
#********************************

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


#********************************
#* Tests securite API          *
#********************************

def test_predict_requires_api_key():
    # Nouveau client sans API key par défaut.
    unauthenticated_client = TestClient(app)

    response = unauthenticated_client.post("/predict", json=get_valid_payload())

    assert response.status_code == 401
    assert response.json() == {"detail": "L'API key manque ou est invalide"}


def test_predict_rejects_invalid_api_key():
    # Remplace volontairement la bonne clé API par une mauvaise.
    response = client.post(
        "/predict",
        json=get_valid_payload(),
        headers={os.environ["API_KEY_HEADER_NAME"]: "invalid-api-key"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "L'API key manque ou est invalide"}


#********************************
#* Tests fonctionnels prediction *
#********************************

def test_predict_success():
    response = client.post("/predict", json=get_valid_payload())

    assert response.status_code == 200
    data = response.json()

    assert set(data.keys()) == {"prediction", "probability", "threshold", "label"} # Marche même si les éléments ne sont pas dans le bon ordre
    assert data["prediction"] in [0, 1]
    assert 0 <= data["probability"] <= 1
    assert 0 <= data["threshold"] <= 1
    assert data["label"] in ["risque_attrition_important", "risque_attrition_faible"]


@pytest.mark.parametrize("case_name", ["stable_profile", "at_risk_profile"]) # Pour lancer le test plusieurs fois avec des valeurs différentes
def test_predict_functional_cases(case_name):
    # Teste deux cas métier connus avec leurs résultats attendus.
    case = get_functional_case(case_name)

    response = client.post("/predict", json=case["payload"])

    assert response.status_code == 200
    data = response.json()

    assert data["prediction"] == case["expected_prediction"]
    assert data["label"] == case["expected_label"]
    assert 0 <= data["probability"] <= 1
    assert 0 <= data["threshold"] <= 1


#********************************
#* Tests tracabilite DB         *
#********************************

def test_predict_logs_request_and_response(db_session):
    payload = get_valid_payload()

    # Insère un salarié en base de test.
    employee = Employee(id_employee=2068, **payload)
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)

    # Appelle /predict avec l'identifiant métier du salarié.
    payload["id_employee"] = employee.id_employee

    response = client.post("/predict", json=payload)

    assert response.status_code == 200

    # Vérifie qu'un input et un output ont bien été historisés.
    input_log = db_session.query(PredictionInputLog).one()
    output_log = db_session.query(PredictionOutputLog).one()

    assert input_log.id_employee == employee.id_employee
    assert output_log.prediction_input_id == input_log.id
    assert output_log.prediction in [0, 1]
    assert 0 <= output_log.probability <= 1
    assert output_log.label in ["risque_attrition_important", "risque_attrition_faible"]


def test_predict_without_matching_employee_still_succeeds(db_session):
    # Aucun salarié n'est inséré en base.
    payload = get_functional_case("at_risk_profile")["payload"]

    response = client.post("/predict", json=payload)

    assert response.status_code == 200

    input_log = db_session.query(PredictionInputLog).one()
    output_log = db_session.query(PredictionOutputLog).one()

    assert input_log.id_employee is None
    assert output_log.prediction_input_id == input_log.id


def test_predict_unknown_id_employee_returns_404():
    # Si un id_employee est explicitement fourni mais inconnu, l'API renvoie 404.
    response = client.post("/predict", json=get_invalid_payload("unknown_id_employee"))

    assert response.status_code == 404
    assert response.json() == {"detail": "L'employé 999999 n'a pas été trouvé"}


def test_predict_success_without_database_tracking(monkeypatch, db_session):
    # Simule une indisponibilité de la base lors du matching salarié.
    def raise_db_error(*args, **kwargs):
        raise SQLAlchemyError("database unavailable")

    monkeypatch.setattr(routes, "find_matching_employee", raise_db_error)

    response = client.post("/predict", json=get_valid_payload())

    assert response.status_code == 200
    assert db_session.query(PredictionInputLog).count() == 0
    assert db_session.query(PredictionOutputLog).count() == 0


#********************************
#* Tests validation Pydantic    *
#********************************

def test_predict_missing_field():
    payload = get_valid_payload()
    payload.pop("age")

    response = client.post("/predict", json=payload)

    assert response.status_code == 422


def test_predict_invalid_type():
    response = client.post("/predict", json=get_invalid_payload("invalid_type_age"))

    assert response.status_code == 422


def test_predict_out_of_range_value():
    response = client.post(
        "/predict",
        json=get_invalid_payload("out_of_range_satisfaction"),
    )

    assert response.status_code == 422


def test_predict_invalid_category():
    response = client.post(
        "/predict",
        json=get_invalid_payload("invalid_category_gender"),
    )

    assert response.status_code == 422


def test_predict_invalid_percentage():
    response = client.post("/predict", json=get_invalid_payload("invalid_percentage"))

    assert response.status_code == 422
