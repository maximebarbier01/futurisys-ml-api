---
title: Futurisys ML API
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# Futurisys ML API

## Présentation

Ce projet est un Proof of Concept visant à déployer un modèle de machine learning issu du projet OpenClassrooms "Classifier automatiquement des informations".

L'objectif est de rendre le modèle accessible via une API FastAPI, avec une structure de code propre, des tests automatisés, une base PostgreSQL et une configuration CI/CD.

## Stack technique

- Python 3.11
- WSL2 Ubuntu 24.04 LTS
- Conda
- Poetry
- FastAPI
- Pytest
- PostgreSQL
- Git / GitHub

## Installation

```bash
cd ~/projects/futurisys-ml-api
conda create -n futurisys-ml-api python=3.11 -y
conda activate futurisys-ml-api
poetry env use $(which python)
poetry install
```

## Protection de la branche principale

La branche `main` est protégée afin de garantir la stabilité de la version principale du projet.

Les règles mises en place sont les suivantes :

- toute modification doit passer par une Pull Request ;
- le job GitHub Actions `test` doit réussir avant fusion ;
- la branche de travail doit être à jour avec `main` avant le merge.

Cette configuration empêche l’intégration d’un code qui ne passe pas les tests automatiques.

## API déployée

L'API est déployée sur Hugging Face Spaces via Docker.

- URL de l'application : https://mxmbrbr-futurisys-ml-api.hf.space
- Documentation Swagger : https://mxmbrbr-futurisys-ml-api.hf.space/docs
- Health check : https://mxmbrbr-futurisys-ml-api.hf.space/health

Le déploiement est automatisé avec GitHub Actions : lorsqu'une Pull Request est fusionnée dans la branche `main`, le workflow CD synchronise le dépôt GitHub vers Hugging Face Spaces.

## Exemple d'appel à l'API

Endpoint :

```http
POST /predict
```

Exemple de requête avec `curl` :

```bash
curl -X POST "https://mxmbrbr-futurisys-ml-api.hf.space/predict" \
  -H "Content-Type: application/json" \
  -d '{
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
    "frequence_deplacement": "Voyage rarement"
  }'
```

Exemple de réponse :

```json
{
  "prediction": 1,
  "probability": 0.73,
  "threshold": 0.211717,
  "label": "attrition"
}
```

## Interprétation de la réponse

- `prediction = 1` : le modèle prédit un risque d'attrition.
- `prediction = 0` : le modèle prédit une absence d'attrition.
- `probability` : probabilité estimée d'attrition.
- `threshold` : seuil de décision retenu lors de l'entraînement.
- `label` : libellé lisible de la prédiction.

## Lancer l'API en local

```bash
uvicorn app.main:app --reload
```

Documentation Swagger locale :

```text
http://127.0.0.1:8000/docs
```

## Lancer les tests

```bash
pytest
```

Avec couverture :

```bash
pytest --cov=app --cov-report=term-missing tests/
```