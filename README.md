---
title: Futurisys ML API
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

<a id="readme-top"></a>

# Futurisys ML API

Proof of Concept realise dans le cadre du parcours OpenClassrooms pour deployer
un modele de machine learning via une API FastAPI, avec validation, tests,
traceabilite locale en base et deploiement automatise.

## Table des matieres

- [A propos du projet](#a-propos-du-projet)
- [Architecture](#architecture)
- [Stack technique](#stack-technique)
- [Demarrage rapide](#demarrage-rapide)
- [Base de donnees PostgreSQL](#base-de-donnees-postgresql)
- [Utilisation de l'API](#utilisation-de-lapi)
- [Documentation du modele](#documentation-du-modele)
- [Tests](#tests)
- [CI/CD et deploiement](#cicd-et-deploiement)
- [Traceabilite des predictions](#traceabilite-des-predictions)
- [Limites et ameliorations](#limites-et-ameliorations)
- [Auteur](#auteur)

## A propos du projet

Ce projet a pour objectif de rendre exploitable en production un modele de
machine learning issu du projet OpenClassrooms
**"Classifier automatiquement des informations"**.

L'API predit le risque d'attrition d'un collaborateur a partir de variables RH.
Le modele est charge depuis un artefact Joblib deja entraine, puis expose via
une interface REST documentee avec Swagger/OpenAPI.

Le projet couvre :

- l'exposition du modele via FastAPI ;
- la validation des entrees avec Pydantic ;
- la persistance locale dans PostgreSQL ;
- les tests unitaires et fonctionnels avec Pytest ;
- l'integration continue avec GitHub Actions ;
- le deploiement sur Hugging Face Spaces via Docker.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Architecture

```text
Client
  ↓
FastAPI
  ↓
Validation Pydantic
  ↓
Service ML
  ↓
Modele Joblib
  ↓
Reponse API

En parallele :
  - journalisation des inputs dans PostgreSQL
  - journalisation des outputs dans PostgreSQL
```

Structure principale du projet :

```text
futurisys-ml-api/
├── app/
│   ├── api/
│   │   └── routes.py
│   ├── db/
│   │   ├── database.py
│   │   ├── models.py
│   │   └── repository.py
│   ├── schemas/
│   │   └── prediction.py
│   ├── services/
│   │   └── model_service.py
│   └── main.py
├── docs/
│   ├── database_schema.md
│   └── model_documentation.md
├── model/
│   └── final_model.joblib
├── scripts/
│   ├── create_db.py
│   └── load_dataset.py
├── sql/
│   └── schema.sql
├── tests/
│   ├── data/
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_database.py
│   ├── test_model_service.py
│   └── test_repository.py
├── .github/workflows/
│   ├── ci.yml
│   └── deploy-hf.yml
├── Dockerfile
├── pyproject.toml
└── README.md
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

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
- Docker
- GitHub Actions
- Hugging Face Spaces

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Demarrage rapide

### Prerequis

- Python 3.11
- Conda ou un environnement virtuel Python
- Poetry
- PostgreSQL en local
- Git

### Installation

1. Cloner le depot

```bash
git clone git@github.com:maximebarbier01/futurisys-ml-api.git
cd futurisys-ml-api
```

2. Creer l'environnement Python

```bash
conda create -n futurisys-ml-api python=3.11 -y
conda activate futurisys-ml-api
```

3. Installer les dependances

```bash
poetry env use $(which python)
poetry install
```

4. Regenerer les fichiers `requirements` si necessaire

```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
poetry export --with dev -f requirements.txt --output requirements-dev.txt --without-hashes
```

### Configuration

Le projet lit la variable `DATABASE_URL` depuis un fichier `.env`.

Exemple de `.env.example` :

```env
DATABASE_URL=postgresql://user:password@localhost:5432/futurisys_ml_api
```

Exemple de `.env` local :

```env
DATABASE_URL=postgresql://futurisys_user:futurisys_password@localhost:5432/futurisys_ml_api
```

Si ton mot de passe contient `@`, il faut l'encoder dans l'URL, par exemple
`%40`.

### Lancer l'API

```bash
uvicorn app.main:app --reload
```

Acces local :

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`
- `http://127.0.0.1:8000/health`

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Base de donnees PostgreSQL

Le projet utilise PostgreSQL en local pour :

- stocker le dataset RH importe ;
- tracer les inputs envoyes au modele ;
- tracer les outputs produits par le modele.

### Creation de la base

```bash
sudo service postgresql start
sudo -u postgres psql
```

Puis dans `psql` :

```sql
CREATE DATABASE futurisys_ml_api;
CREATE USER futurisys_user WITH PASSWORD 'futurisys_password';
GRANT ALL PRIVILEGES ON DATABASE futurisys_ml_api TO futurisys_user;
\q
```

### Creation des tables

```bash
python scripts/create_db.py
```

### Import du dataset

```bash
python scripts/load_dataset.py --csv-path /path/to/data_eda.csv --truncate
```

### Schema de base

- documentation : `docs/database_schema.md`
- version SQL : `sql/schema.sql`

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Utilisation de l'API

### Endpoints disponibles

| Methode | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Verifie que l'API repond |
| `GET` | `/health` | Verifie l'etat de sante |
| `POST` | `/predict` | Retourne une prediction d'attrition |

### Documentation interactive

La documentation Swagger/OpenAPI est disponible ici :

- local : `http://127.0.0.1:8000/docs`
- deployee : [mxmbrbr-futurisys-ml-api.hf.space/docs](https://mxmbrbr-futurisys-ml-api.hf.space/docs)

### Exemple de requete

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
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
    "heure_supplementaires": 1,
    "augementation_salaire_precedente": 0.14,
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

### Exemple de reponse

```json
{
  "prediction": 1,
  "probability": 0.73,
  "threshold": 0.211717,
  "label": "attrition"
}
```

### Validation des entrees

Le schema Pydantic :

- verifie les champs obligatoires ;
- controle les types ;
- impose des bornes metier ;
- restreint certaines categories avec `Literal[...]` ;
- accepte un `employee_id` optionnel pour lier une prediction a un employe existant.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Documentation du modele

### Role du modele

Le modele realise une **classification binaire** :

- `0` : `non_attrition`
- `1` : `attrition`

### Artefact deploye

Le modele final est charge depuis :

```text
model/final_model.joblib
```

Cet artefact contient :

- le pipeline de prediction ;
- le seuil de decision metier ;
- la liste des variables attendues en entree ;
- les eventuelles metadonnees de version.

### Sortie du modele

L'API retourne toujours quatre informations :

- `prediction` : classe finale ;
- `probability` : probabilite de la classe positive ;
- `threshold` : seuil applique ;
- `label` : libelle metier associe.

### Maintenance du modele

Protocole recommande pour une mise a jour :

1. mettre a jour le dataset source ;
2. relancer la preparation et l'entrainement ;
3. recalculer les metriques de performance ;
4. valider ou ajuster le seuil metier ;
5. exporter un nouvel artefact `final_model.joblib` ;
6. relancer la suite de tests ;
7. redeployer l'API.

### Performances

Ce depot contient l'artefact deploye et toute la couche d'exposition de l'API.
Les metriques detaillees du modele doivent etre reprises depuis le travail de
modelisation du projet P4 si tu veux les afficher dans une documentation plus
complete ou dans le support de soutenance.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Tests

Le projet contient des tests unitaires et fonctionnels :

- `tests/test_api.py` : tests fonctionnels API ;
- `tests/test_model_service.py` : tests unitaires du service ML ;
- `tests/test_repository.py` : tests unitaires de la couche repository ;
- `tests/test_database.py` : tests du cycle de vie de la session DB ;
- `tests/data/` : jeux de donnees de test.

### Lancer les tests

```bash
pytest
```

### Lancer les tests avec couverture

```bash
pytest --cov=app --cov-report=term-missing tests/
```

### Generer les rapports HTML et XML

```bash
pytest --cov=app --cov-report=term-missing --cov-report=html --cov-report=xml tests/
```

Rapports generes :

- `htmlcov/`
- `coverage.xml`

Etat actuel :

- 29 tests
- 100% de couverture sur `app`

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## CI/CD et deploiement

### Integration continue

Workflow : `/.github/workflows/ci.yml`

Fonctionnement :

- declenche sur `push` vers toutes les branches ;
- declenche sur `pull_request` vers `main` et `develop` ;
- installe Python 3.11 ;
- installe les dependances ;
- lance Pytest avec couverture minimale.

### Deploiement continu

Workflow : `/.github/workflows/deploy-hf.yml`

Fonctionnement :

- declenche sur `push` vers `main` ;
- declenchable manuellement avec `workflow_dispatch` ;
- synchronise le depot vers Hugging Face Spaces.

### Secret GitHub utilise

```text
HF_TOKEN
```

### Deploiement Hugging Face

- application : [mxmbrbr-futurisys-ml-api.hf.space](https://mxmbrbr-futurisys-ml-api.hf.space)
- Swagger : [mxmbrbr-futurisys-ml-api.hf.space/docs](https://mxmbrbr-futurisys-ml-api.hf.space/docs)
- health check : [mxmbrbr-futurisys-ml-api.hf.space/health](https://mxmbrbr-futurisys-ml-api.hf.space/health)

### Comportement sur Hugging Face

Le Space peut fonctionner sans PostgreSQL disponible. Dans ce cas :

- `/predict` continue de retourner une prediction ;
- la persistance dans `prediction_inputs` et `prediction_outputs` est ignoree ;
- la traceabilite complete reste reservee a l'execution locale ou a un deploiement avec une base PostgreSQL accessible.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Traceabilite des predictions

Le projet garantit une traceabilite locale des inferences :

- les donnees source sont stockees dans `employees` ;
- chaque payload recu par `/predict` est stocke dans `prediction_inputs` ;
- chaque resultat retourne est stocke dans `prediction_outputs`.

Si `employee_id` est fourni dans le payload :

- la prediction est liee directement a l'employe concerne.

Sinon :

- l'API tente un matching exact avec les donnees deja presentes en base.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Limites et ameliorations

- PostgreSQL est prevu principalement pour un usage local dans ce POC.
- Hugging Face Spaces ne garantit pas une traceabilite PostgreSQL complete sans base externe.
- L'API ne gere pas encore d'authentification dediee.
- Un endpoint `/predict/by-employee/{employee_id}` pourrait etre ajoute plus tard.
- Le protocole de reentrainement du modele peut encore etre davantage automatise.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Auteur

Maxime Barbier

Projet GitHub :
[https://github.com/maximebarbier01/futurisys-ml-api](https://github.com/maximebarbier01/futurisys-ml-api)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
