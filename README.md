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
via une API FastAPI, testable localement et deployable sur Hugging Face Spaces.

L'API predit le risque d'attrition d'un collaborateur a partir de donnees RH.
Le modele est charge depuis un artefact Joblib deja entraine, puis expose via
une interface REST documentee avec Swagger/OpenAPI.

## Fonctionnalites principales

- API FastAPI avec les endpoints `/`, `/health` et `/predict`
- Validation forte des payloads avec Pydantic
- Chargement du modele depuis `model/final_model.joblib`
- Traceabilite locale des appels dans PostgreSQL
- Import du dataset RH dans une table `employees`
- Tests unitaires et fonctionnels avec Pytest
- Rapport de couverture via `pytest-cov`
- CI avec GitHub Actions
- CD vers Hugging Face Spaces via Docker

## Stack technique

- Python 3.11
- FastAPI
- Pydantic v2
- pandas
- scikit-learn
- LightGBM
- SQLAlchemy
- PostgreSQL
- Joblib
- Pytest
- Pytest-cov
- GitHub Actions
- Docker
- Hugging Face Spaces

## Structure du projet

```text
futurisys-ml-api/
|- app/
|  |- api/
|  |  `- routes.py
|  |- db/
|  |  |- database.py
|  |  |- models.py
|  |  `- repository.py
|  |- schemas/
|  |  `- prediction.py
|  |- services/
|  |  `- model_service.py
|  `- main.py
|- docs/
|  `- database_schema.md
|- model/
|  `- final_model.joblib
|- scripts/
|  |- create_db.py
|  `- load_dataset.py
|- sql/
|  `- schema.sql
|- tests/
|  |- data/
|  |- conftest.py
|  |- test_api.py
|  |- test_database.py
|  |- test_model_service.py
|  `- test_repository.py
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
- la liste des variables attendues en entree ;
- les metadonnees de version du modele.

L'API ne reentraine pas le modele. Elle charge simplement l'artefact au
demarrage, transforme la requete JSON en `DataFrame` pandas, puis renvoie une
prediction binaire accompagnee de sa probabilite.

## Installation locale

### 1. Cloner le depot

```bash
git clone git@github.com:maximebarbier01/futurisys-ml-api.git
cd futurisys-ml-api
```

### 2. Creer et activer un environnement Python 3.11

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

## Configuration locale

Le projet lit la variable `DATABASE_URL` depuis un fichier `.env`.

### `.env.example`

```env
DATABASE_URL=postgresql://user:password@localhost:5432/futurisys_ml_api
```

### Exemple de `.env` local

```env
DATABASE_URL=postgresql://futurisys_user:futurisys_password@localhost:5432/futurisys_ml_api
```

Si ton mot de passe contient `@`, il faut l'encoder dans l'URL. Exemple :

```env
DATABASE_URL=postgresql://futurisys_user:%40udrey29Le@localhost:5432/futurisys_ml_api
```

## Base PostgreSQL locale

L'interaction avec PostgreSQL est prevue pour un usage local dans ce POC.

### 1. Demarrer PostgreSQL

```bash
sudo service postgresql start
```

### 2. Creer la base et l'utilisateur

```bash
sudo -u postgres psql
```

Puis dans `psql` :

```sql
CREATE DATABASE futurisys_ml_api;
CREATE USER futurisys_user WITH PASSWORD 'futurisys_password';
GRANT ALL PRIVILEGES ON DATABASE futurisys_ml_api TO futurisys_user;
\q
```

### 3. Creer les tables

```bash
python scripts/create_db.py
```

### 4. Importer le dataset RH

```bash
python scripts/load_dataset.py --csv-path /path/to/data_eda.csv --truncate
```

### 5. Schema de base de donnees

- documentation : `docs/database_schema.md`
- version SQL : `sql/schema.sql`

## Traceabilite des predictions

Le schema PostgreSQL repose sur trois tables principales :

- `employees` : dataset RH importe en base
- `prediction_inputs` : payloads envoyes au modele
- `prediction_outputs` : resultats retournes par le modele

Workflow de traceabilite :

1. Le dataset source est charge dans `employees`.
2. Un appel API vers `/predict` cree une ligne dans `prediction_inputs`.
3. Le resultat de prediction est stocke dans `prediction_outputs`.
4. Si `employee_id` est fourni dans le payload, il est utilise pour relier la prediction a `employees`.
5. Si `employee_id` n'est pas fourni, l'API tente un matching exact sur les variables du payload.

## Lancer l'API en local

```bash
uvicorn app.main:app --reload
```

L'API est alors disponible sur :

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`
- `http://127.0.0.1:8000/health`

## Endpoints disponibles

| Methode | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Verifie que l'API est accessible |
| `GET` | `/health` | Verifie l'etat de sante de l'API |
| `POST` | `/predict` | Retourne une prediction d'attrition |

## Validation des donnees

Le payload attendu est defini dans `app/schemas/prediction.py` via un schema
Pydantic.

Le schema :

- impose les champs obligatoires ;
- verifie les types numeriques ;
- controle les bornes metier ;
- restreint certaines categories avec `Literal[...]` ;
- accepte un `employee_id` optionnel pour tracer une prediction sur un employe existant.

La documentation Swagger propose un exemple complet d'entree pour faciliter les
tests manuels.

## Exemple d'appel local a l'API

Exemple de requete avec `curl` :

```bash
curl -X POST "http://127.0.0.1:8000/predict"   -H "Content-Type: application/json"   -d '{
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
    "heure_supplementaires": 1,
    "augementation_salaire_precedente": 0.14,
    "nombre_participation_pee": 1,
    "nb_formations_suivies": 3,
    "distance_domicile_travail": 12,
    "niveau_education": 4,
    "annees_depuis_la_derniere_promotion": 1,
    "annes_sous_responsable_actuel": 2,
    "genre": "M",
    "statut_marital": "Mari\u00e9(e)",
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

## Deploiement sur Hugging Face Spaces

L'application est deployee sur Hugging Face Spaces via Docker :

- application : [mxmbrbr-futurisys-ml-api.hf.space](https://mxmbrbr-futurisys-ml-api.hf.space)
- Swagger : [mxmbrbr-futurisys-ml-api.hf.space/docs](https://mxmbrbr-futurisys-ml-api.hf.space/docs)
- health check : [mxmbrbr-futurisys-ml-api.hf.space/health](https://mxmbrbr-futurisys-ml-api.hf.space/health)

Le deploiement est automatise depuis GitHub Actions lors d'un `push` sur `main`.

### Comportement sur Hugging Face

Le Space peut fonctionner sans PostgreSQL disponible. Dans ce cas :

- `/predict` continue de retourner une prediction ;
- la persistance dans `prediction_inputs` et `prediction_outputs` est ignoree ;
- la traceabilite complete reste donc reservee a l'execution locale ou a un deploiement avec une base PostgreSQL accessible.

## Docker

Le deploiement Hugging Face Spaces repose sur le `Dockerfile` du projet.

Le conteneur :

- utilise `python:3.11-slim` ;
- installe `libgomp1` pour LightGBM ;
- installe les dependances depuis `requirements.txt` ;
- lance Uvicorn sur le port `7860`.

Commande executee dans le conteneur :

```bash
uvicorn app.main:app --host 0.0.0.0 --port 7860
```

## Tests

Le projet contient des tests unitaires et fonctionnels :

- `tests/test_api.py` : tests fonctionnels API
- `tests/test_model_service.py` : tests unitaires du service ML
- `tests/test_repository.py` : tests unitaires de la couche repository
- `tests/test_database.py` : tests du cycle de vie de la session DB
- `tests/data/` : payloads valides, invalides et cas metier

### Lancer les tests

```bash
pytest
```

### Couverture simple

```bash
pytest --cov=app --cov-report=term-missing tests/
```

### Rapports de couverture HTML et XML

```bash
pytest --cov=app --cov-report=term-missing --cov-report=html --cov-report=xml tests/
```

Les rapports generes sont :

- `htmlcov/`
- `coverage.xml`

Sur cette branche, la suite contient actuellement 29 tests et couvre 100 % du
package `app`.

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

- `push` sur toutes les branches ;
- `pull_request` vers `main` et `develop`.

### Deploiement continu

Fichier :

```text
.github/workflows/deploy-hf.yml
```

Le workflow CD :

- se declenche sur `push` vers `main` ;
- peut aussi etre lance manuellement avec `workflow_dispatch` ;
- synchronise le depot GitHub vers Hugging Face Spaces.

### Secret GitHub utilise

```text
HF_TOKEN
```

## Workflow Git

Organisation actuelle des branches :

- `main` : branche stable deployee
- `develop` : branche d'integration
- `feature/*` : nouvelles fonctionnalites
- `fix/*` : corrections
- `docs/*` : documentation
- `style/*` : harmonisation visuelle et lisibilite du code

Exemples :

```bash
git switch -c feature/api-fastapi
git switch -c feature/postgresql-tracking
git switch -c fix/hf-predict-without-db
git switch -c docs/update-readme
git switch -c style/code-clarity-sections
```

Convention de messages de commit :

```text
feat: ajout d'une fonctionnalite
fix: correction d'un bug
docs: modification de la documentation
refactor: amelioration de la structure du code sans changement fonctionnel
test: ajout ou modification de tests
ci: modification de la configuration CI/CD
chore: tache technique ou maintenance
```

## Limites connues

- PostgreSQL est pense pour un usage local dans ce POC.
- Le Space Hugging Face n'offre pas de traceabilite PostgreSQL complete sans base externe configuree.
- Il n'y a pas encore d'authentification API dediee.
- Un endpoint du type `/predict/by-employee/{employee_id}` pourrait etre ajoute plus tard pour simplifier les usages relies a la base.

## Statut du projet

Fonctionnalites deja en place sur cette branche :

- API FastAPI fonctionnelle ;
- chargement du modele depuis un artefact Joblib ;
- endpoint `/predict` operationnel ;
- validation robuste avec Pydantic ;
- persistance PostgreSQL locale des predictions ;
- documentation Swagger generee automatiquement ;
- tests unitaires et fonctionnels ;
- pipeline CI GitHub Actions ;
- deploiement Docker sur Hugging Face Spaces.
