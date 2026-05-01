from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def get_valid_payload():
    return {
        "age": 35,
        "revenu_mensuel": 4200,
        "nombre_experiences_precedentes": 2,
        "annee_experience_totale": 10,
        "annees_dans_l_entreprise": 5,
        "annees_dans_le_poste_actuel": 3,
        "satisfaction_employee_environnement": 3,
        "satisfaction_employee_nature_travail": 4,
        "satisfaction_employee_equipe": 3,
        "satisfaction_employee_equilibre_pro_perso": 2,
        "note_evaluation_precedente": 3,
        "note_evaluation_actuelle": 4,
        "niveau_hierarchique_poste": 2,
        "heure_supplementaires": 0,
        "augementation_salaire_precedente": 12,
        "nombre_participation_pee": 1,
        "nb_formations_suivies": 2,
        "distance_domicile_travail": 8,
        "niveau_education": 3,
        "annees_depuis_la_derniere_promotion": 1,
        "annes_sous_responsable_actuel": 3,
        "genre": "Homme",
        "statut_marital": "Marié",
        "departement": "Recherche & Développement",
        "poste": "Ingénieur de recherche",
        "domaine_etude": "Sciences de la vie",
        "frequence_deplacement": "Voyage rarement",
    }


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

    assert response.status_code == 422  # validation Pydantic


def test_health():
    response = client.get("/health")
    assert response.status_code == 200