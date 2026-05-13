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

## Presentation

Ce projet est un Proof of Concept realise dans le cadre du parcours OpenClassrooms.

L'objectif est de deployer un modele de machine learning issu du projet
**"Classifier automatiquement des informations"** afin de le rendre exploitable
via une API FastAPI.

L'API predit le risque d'attrition d'un collaborateur a partir de donnees RH.
Le modele est charge depuis un artefact Joblib deja entraine, puis expose via
une interface REST documentee avec Swagger/OpenAPI.

Le projet met deja en place plusieurs bonnes pratiques d'ingenierie logicielle :

- structuration claire du depot ;
- gestion des dependances avec Poetry ;
- validation des entrees avec Pydantic ;
- tests automatises avec Pytest ;
- integration continue avec GitHub Actions ;
- deploiement continu vers Hugging Face Spaces avec Docker.

## Stack technique

- Python 3.11
- FastAPI
- Pydantic
- pandas
- scikit-learn
- LightGBM
- Joblib
- Pytest
- GitHub Actions
- Docker
- Hugging Face Spaces

## Structure du projet

```text
futurisys-ml-api/
|- app/
|  |- api/
|  |  `- routes.py
|  |- schemas/
|  |  `- prediction.py
|  |- services/
|  |  `- model_service.py
|  `- main.py
|- model/
|  `- final_model.joblib
|- tests/
|  |- conftest.py
|  `- test_api.py
|- .github/
|  `- workflows/
|     |- ci.yml
|     `- deploy-hf.yml
|- Dockerfile
|- README.md
|- pyproject.toml
|- poetry.lock
|- requirements.txt
`- requirements-dev.txt
```

## Modele de machine learning

Le modele final est stocke dans :

```text
model/final_model.joblib
```

L'artefact contient :

- le pipeline de prediction ;
- le seuil de decision metier ;
- la liste des variables attendues en entree.

L'API ne reentraine pas le modele. Elle charge simplement l'artefact au
demarrage, transforme la requete JSON en `DataFrame` pandas, puis renvoie une
prediction binaire accompagnee de sa probabilite.

## Installation locale

### 1. Cloner le depot

```bash
git clone git@github.com:maximebarbier01/futurisys-ml-api.git
cd futurisys-ml-api
```

### 2. Creer l'environnement Python

Avec Conda :

```bash
conda create -n futurisys-ml-api python=3.11 -y
conda activate futurisys-ml-api
```

### 3. Installer les dependances avec Poetry

```bash
poetry env use $(which python)
poetry install
```

### 4. Regenerer les fichiers requirements si necessaire

```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
poetry export --with dev -f requirements.txt --output requirements-dev.txt --without-hashes
```

## Lancer l'API en local

```bash
uvicorn app.main:app --reload
```

L'API est alors disponible sur :

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`
- `http://127.0.0.1:8000/health`

## API deployee

L'application est deployee sur Hugging Face Spaces via Docker :

- application : [mxmbrbr-futurisys-ml-api.hf.space](https://mxmbrbr-futurisys-ml-api.hf.space)
- Swagger : [mxmbrbr-futurisys-ml-api.hf.space/docs](https://mxmbrbr-futurisys-ml-api.hf.space/docs)
- health check : [mxmbrbr-futurisys-ml-api.hf.space/health](https://mxmbrbr-futurisys-ml-api.hf.space/health)

Le deploiement est automatise par GitHub Actions lors d'un `push` sur `main`.

## Endpoints disponibles

| Methode | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Verifie que l'API est accessible |
| `GET` | `/health` | Verifie l'etat de sante de l'API |
| `POST` | `/predict` | Retourne une prediction d'attrition |

## Exemple d'appel a l'API

Exemple de requete avec `curl` :

```bash
curl -X POST "https://mxmbrbr-futurisys-ml-api.hf.space/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 38,
    "revenu_mensuel": 5400,
    "nombre_experiences_precedentes": 3,
    "annee_experience_totale": 12,
    "annees_dans_l_entreprise": 4,
    "annees_dans_le_poste_actuel": 2,
    "satisfaction_employee_environnement": 3,
    "satisfaction_employee_nature_travail": 4,
    "satisfaction_employee_equipe": 4,
    "satisfaction_employee_equilibre_pro_perso": 3,
    "note_evaluation_precedente": 3,
    "note_evaluation_actuelle": 4,
    "niveau_hierarchique_poste": 2,
    "heure_supplementaires": 0,
    "augementation_salaire_precedente": 0.12,
    "nombre_participation_pee": 1,
    "nb_formations_suivies": 3,
    "distance_domicile_travail": 12,
    "niveau_education": 4,
    "annees_depuis_la_derniere_promotion": 1,
    "annes_sous_responsable_actuel": 2,
    "genre": "M",
    "statut_marital": "Marié(e)",
    "departement": "Consulting",
    "poste": "Consultant",
    "domaine_etude": "Transformation Digitale",
    "frequence_deplacement": "Occasionnel"
  }'
```

Exemple de reponse :

```json
{
  "prediction": 1,
  "probability": 0.73,
  "threshold": 0.211717,
  "label": "attrition"
}
```

## Validation des donnees

Le payload attendu est defini dans
[app/schemas/prediction.py](/mnt/wslg/distro/home/maxime/projects/futurisys-ml-api/app/schemas/prediction.py)
via un schema Pydantic.

La documentation Swagger propose un exemple complet d'entree pour faciliter les
tests manuels.

## Lancer les tests

Tests simples :

```bash
pytest
```

Tests avec couverture :

```bash
pytest --cov=app --cov-report=term-missing --cov-fail-under=70 tests/
```

Les tests couvrent actuellement :

- l'endpoint `/predict` sur un cas nominal ;
- la validation d'un champ obligatoire manquant ;
- l'endpoint `/health`.

## CI/CD

Le projet utilise deux workflows GitHub Actions.

### Integration continue

Fichier :

```text
.github/workflows/ci.yml
```

Le workflow CI :

- installe Python 3.11 ;
- installe les dependances depuis `requirements-dev.txt` ;
- execute Pytest ;
- verifie une couverture minimale de 70 %.

Declenchement actuel :

- `push` sur `main`, `develop` et `feature/*` ;
- `pull_request` vers `main` et `develop`.

### Deploiement continu

Fichier :

```text
.github/workflows/deploy-hf.yml
```

Le workflow CD synchronise le depot GitHub vers Hugging Face Spaces.

Declenchement actuel :

- `push` sur `main` ;
- execution manuelle possible avec `workflow_dispatch`.

### Secret GitHub utilise

```text
HF_TOKEN
```

## Docker

Le deploiement Hugging Face Spaces repose sur le
[Dockerfile](/mnt/wslg/distro/home/maxime/projects/futurisys-ml-api/Dockerfile).

Le conteneur :

- utilise `python:3.11-slim` ;
- installe `libgomp1` pour LightGBM ;
- installe les dependances depuis `requirements.txt` ;
- lance Uvicorn sur le port `7860`.

Commande executee dans le conteneur :

```bash
uvicorn app.main:app --host 0.0.0.0 --port 7860
```

## Workflow Git

Organisation actuelle des branches :

- `main` : branche stable deployee ;
- `feature/*` : nouvelles fonctionnalites ;
- `fix/*` : corrections ;
- `docs/*` : documentation.

Exemples :

```bash
git checkout -b feature/api-fastapi
git checkout -b fix/hf-lightgbm-runtime
git checkout -b docs/update-readme
```

Convention de messages de commit :

```text
feat: ajout d'une fonctionnalite
fix: correction d'un bug
docs: modification de la documentation
test: ajout ou modification de tests
ci: modification de la configuration CI/CD
chore: tache technique ou maintenance
```

## Roadmap

Les prochaines evolutions prevues du projet sont :

- durcir davantage la validation Pydantic des entrees ;
- ajouter la persistance PostgreSQL des inputs et outputs de prediction ;
- enrichir les tests d'API et la couverture fonctionnelle ;
- documenter le schema de base de donnees et le chargement du dataset.

## Statut du projet

Fonctionnalites deja en place sur cette branche :

- API FastAPI fonctionnelle ;
- chargement du modele depuis un artefact Joblib ;
- endpoint `/predict` operationnel ;
- documentation Swagger generee automatiquement ;
- tests Pytest ;
- pipeline CI GitHub Actions ;
- deploiement Docker sur Hugging Face Spaces.
