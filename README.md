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

Proof of Concept réalisé dans le cadre du parcours OpenClassrooms pour déployer
un modèle de machine learning via une API FastAPI, avec validation, tests,
traçabilité locale en base et déploiement automatisé.

## Table des matières

- [À propos du projet](#à-propos-du-projet)
- [Architecture](#architecture)
- [Stack technique](#stack-technique)
- [Démarrage rapide](#démarrage-rapide)
- [Utilisation avec Docker en local](#utilisation-avec-docker-en-local)
- [Base de données PostgreSQL](#base-de-données-postgresql)
- [PostgreSQL distant validé](#postgresql-distant-validé)
- [Utilisation de l'API](#utilisation-de-lapi)
- [Documentation du modèle](#documentation-du-modèle)
- [Tests](#tests)
- [CI/CD et déploiement](#cicd-et-déploiement)
- [Traçabilité des prédictions](#traçabilité-des-prédictions)
- [Limites et améliorations](#limites-et-améliorations)
- [Auteur](#auteur)

## À propos du projet

Ce projet a pour objectif de rendre exploitable en production un modèle de
machine learning issu du projet OpenClassrooms
**"Classifier automatiquement des informations"**.

L'API prédit le risque d'attrition d'un collaborateur à partir de variables RH.
Le modèle est chargé depuis un artefact Joblib déjà entraîné, puis exposé via
une interface REST documentée avec Swagger/OpenAPI.

Le projet couvre :

- l'exposition du modèle via FastAPI ;
- la validation des entrées avec Pydantic ;
- la persistance locale dans PostgreSQL ;
- les tests unitaires et fonctionnels avec Pytest ;
- l'intégration continue avec GitHub Actions ;
- le déploiement sur Hugging Face Spaces via Docker.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Architecture

```text
Client
  -> FastAPI
  -> Validation Pydantic
  -> Service ML
  -> Modèle Joblib
  -> Réponse API

En parallèle :
  - journalisation des inputs dans PostgreSQL
  - journalisation des outputs dans PostgreSQL
```

Structure principale du projet :

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
|  |- database_schema.md
|  `- model_documentation.md
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
|- .github/workflows/
|  |- ci.yml
|  `- deploy-hf.yml
|- Dockerfile
|- pyproject.toml
`- README.md
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

## Démarrage rapide

### Prérequis

- Python 3.11
- Conda ou un environnement virtuel Python
- Poetry
- PostgreSQL en local
- Git

### Installation

1. Cloner le dépôt

```bash
git clone git@github.com:maximebarbier01/futurisys-ml-api.git
cd futurisys-ml-api
```

2. Créer l'environnement Python

```bash
conda create -n futurisys-ml-api python=3.11 -y
conda activate futurisys-ml-api
```

3. Installer les dépendances

```bash
poetry env use $(which python)
poetry install
```

4. Régénérer les fichiers `requirements` si nécessaire

```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
poetry export --with dev -f requirements.txt --output requirements-dev.txt --without-hashes
```

### Configuration

Le projet lit sa configuration depuis un fichier `.env`.

Variables attendues :

- `DATABASE_URL`
- `API_KEY`
- `API_KEY_HEADER_NAME`

Exemple de `.env.example` :

```env
DATABASE_URL=postgresql://user:password@localhost:5432/futurisys_ml_api
API_KEY=change-me
API_KEY_HEADER_NAME=X-API-Key
```

Exemple de `.env.local` :

```env
DATABASE_URL=postgresql://futurisys_user:<your-local-password>@localhost:5432/futurisys_ml_api
API_KEY=<local-api-key>
API_KEY_HEADER_NAME=X-API-Key
```

Exemple de `.env.remote` :

```env
DATABASE_URL=postgresql://<remote-user>:<remote-password>@<remote-host>:<remote-port>/<remote-database>
API_KEY=<remote-api-key>
API_KEY_HEADER_NAME=X-API-Key
```

ou :

```bash
cp .env.remote .env
```

### Gestion recommandée des environnements

L'application charge uniquement le fichier `.env` au démarrage.

Pour lancer `uvicorn` avec la configuration locale :

```bash
cp .env.local .env
uvicorn app.main:app --reload
```

Pour lancer `uvicorn` avec la configuration distante :

```bash
cp .env.remote .env
uvicorn app.main:app --reload
```

Cette approche permet de garder plusieurs presets non versionnés et d'activer
simplement celui voulu. Les vrais secrets ne doivent jamais être ajoutés au
`README.md` ni à `.env.example`.

### Lancer l'API

```bash
uvicorn app.main:app --reload
```

Accès local :

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`
- `http://127.0.0.1:8000/health`

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Utilisation avec Docker en local

### Construire l'image

```bash
docker build -t futurisys-ml-api .
```

### Lancer le conteneur avec l'environnement local

```bash
docker run --rm -p 8000:7860 --env-file .env.local futurisys-ml-api
```

### Lancer le conteneur avec l'environnement distant

```bash
docker run --rm -p 8000:7860 --env-file .env.remote futurisys-ml-api
```

### Pourquoi `cp .env.remote .env` ne suffit pas pour Docker

Contrairement à `uvicorn` lancé directement sur la machine locale, Docker ne lit
pas automatiquement le fichier `.env` du projet dans ce dépôt.

Dans cette configuration :

- `.dockerignore` exclut `.env` et `.env.*` du contexte de build ;
- l'image construite n'embarque donc pas ces fichiers ;
- il faut passer explicitement les variables au runtime avec `--env-file` ou
  `-e`.

Autrement dit :

- `cp .env.local .env` ou `cp .env.remote .env` sert à choisir la configuration
  active pour `uvicorn` ;
- `docker run --env-file .env.local ...` ou
  `docker run --env-file .env.remote ...` sert à choisir la configuration
  active pour le conteneur.

### URLs d'accès

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`
- `http://127.0.0.1:8000/health`

### Comportement sans variables passées au conteneur

Si le conteneur est lancé sans `--env-file` ni variables `-e`, il peut ne pas
recevoir la bonne `DATABASE_URL`.

Dans ce cas :

- l'API peut quand même démarrer ;
- `/predict` peut continuer de répondre ;
- la persistance dans `prediction_inputs` et `prediction_outputs` peut être
  ignorée si la base configurée n'est pas joignable ;
- un warning de connexion PostgreSQL peut apparaître dans les logs du conteneur.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Base de données PostgreSQL

Le projet utilise PostgreSQL en local pour :

- stocker le dataset RH importé ;
- tracer les inputs envoyés au modèle ;
- tracer les outputs produits par le modèle.

Les identifiants de connexion ne sont pas stockés dans le code applicatif :
ils sont lus depuis `DATABASE_URL` afin de limiter l'exposition de secrets et
de permettre l'usage d'un utilisateur PostgreSQL dédié.

### Création de la base

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

### Création des tables

```bash
python scripts/create_db.py
```

### Import du dataset

```bash
python scripts/load_dataset.py --csv-path /path/to/data_eda.csv --truncate
```

### Schéma de base

- documentation : `docs/database_schema.md`
- version SQL : `sql/schema.sql`

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## PostgreSQL distant validé

Une instance PostgreSQL distante a été validée avec Supabase afin de confirmer
que la traçabilité ne dépend pas uniquement d'une base locale.

Ce scénario a permis de vérifier que :

- `python scripts/create_db.py` crée correctement les tables à distance ;
- `python scripts/load_dataset.py --csv-path ... --truncate` charge le dataset
  complet dans `employees` ;
- l'API locale branchée sur `.env.remote` enregistre bien les prédictions dans
  `prediction_inputs` et `prediction_outputs` ;
- le conteneur Docker branché sur `--env-file .env.remote` persiste également
  les écritures.

Vérification SQL réalisée après import :

```sql
SELECT COUNT(*) FROM employees;
SELECT COUNT(*) FROM prediction_inputs;
SELECT COUNT(*) FROM prediction_outputs;
```

Résultat observé après chargement initial du dataset :

- `employees = 1470`
- `prediction_inputs = 0`
- `prediction_outputs = 0`

Puis les compteurs des tables de logs augmentent après chaque appel valide à
`/predict`.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Utilisation de l'API

### Endpoints disponibles

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Vérifie que l'API répond |
| `GET` | `/health` | Vérifie l'état de santé |
| `POST` | `/predict` | Retourne une prédiction d'attrition, protégée par clé API |

### Documentation interactive

La documentation Swagger/OpenAPI est disponible ici :

- local : `http://127.0.0.1:8000/docs`
- déployée : [mxmbrbr-futurisys-ml-api.hf.space/docs](https://mxmbrbr-futurisys-ml-api.hf.space/docs)

### Sécurité de l'API

L'endpoint `/predict` peut être protégé par une clé API transmise dans l'en-tête
`X-API-Key`.

L'authentification mise en place repose sur une clé API transmise dans
`X-API-Key`. Elle protège l'endpoint métier `/predict`, tandis que `/` et
`/health` restent publics pour les besoins de supervision.

Variables d'environnement associées :

- `API_KEY` : valeur attendue pour autoriser l'accès ;
- `API_KEY_HEADER_NAME` : nom de l'en-tête HTTP utilisé, `X-API-Key` par
  défaut.

Les secrets applicatifs (`API_KEY`, `DATABASE_URL`) ne doivent jamais être
stockés en dur dans le code ni commités dans le dépôt. Ils doivent être fournis
via des variables d'environnement ou des fichiers `.env` non versionnés.

Ce mécanisme correspond à une sécurité simple adaptée à un POC. En production,
il pourrait être complété par une authentification plus robuste, une gestion
des rôles, une rotation des secrets et une solution de coffre-fort.

### Exemple de requête

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <api-key>" \
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

### Exemple de réponse

```json
{
  "prediction": 1,
  "probability": 0.73,
  "threshold": 0.211717,
  "label": "risque_attrition_important"
}
```

### Validation des entrées

Le schéma Pydantic :

- vérifie les champs obligatoires ;
- contrôle les types ;
- impose des bornes métier ;
- restreint certaines catégories avec `Literal[...]` ;
- accepte un `id_employee` optionnel pour lier une prédiction à un employé existant.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Documentation du modèle

### Rôle du modèle

Le modèle réalise une **classification binaire** :

- `0` : `risque_attrition_faible`
- `1` : `risque_attrition_important`

### Artefact déployé

Le modèle final est chargé depuis :

```text
model/final_model.joblib
```

Cet artefact contient :

- le pipeline de prédiction ;
- le seuil de décision métier ;
- la liste des variables attendues en entrée ;
- les éventuelles métadonnées de version.

### Sortie du modèle

L'API retourne toujours quatre informations :

- `prediction` : classe finale ;
- `probability` : probabilité de la classe positive ;
- `threshold` : seuil appliqué ;
- `label` : libellé métier associé.

### Maintenance du modèle

Protocole recommandé pour une mise à jour :

1. mettre à jour le dataset source ;
2. relancer la préparation et l'entraînement ;
3. recalculer les métriques de performance ;
4. valider ou ajuster le seuil métier ;
5. exporter un nouvel artefact `final_model.joblib` ;
6. relancer la suite de tests ;
7. redéployer l'API.

### Performances

Voir `docs/model_documentation.md`.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Tests

Le projet contient des tests unitaires et fonctionnels :

- `tests/test_api.py` : tests fonctionnels API ;
- `tests/test_model_service.py` : tests unitaires du service ML ;
- `tests/test_repository.py` : tests unitaires de la couche repository ;
- `tests/test_database.py` : tests du cycle de vie de la session DB ;
- `tests/data/` : jeux de données de test.

### Lancer les tests

```bash
pytest
```

### Lancer les tests avec couverture

```bash
pytest --cov=app --cov-report=term-missing tests/
```

### Générer les rapports HTML et XML

```bash
pytest --cov=app --cov-report=term-missing --cov-report=html --cov-report=xml tests/
```

Rapports générés :

- `htmlcov/`
- `coverage.xml`

### Exploiter le rapport de couverture

- `htmlcov/` contient une version navigable du rapport, pensée pour une lecture
  humaine fichier par fichier ;
- `htmlcov/index.html` peut être ouvert localement dans un navigateur pour
  visualiser les lignes couvertes et non couvertes ;
- `coverage.xml` est un format structuré, utile pour la CI, les outils
  d'analyse et le suivi automatisé de la qualité.

Exemple pour ouvrir le rapport HTML sous Linux :

```bash
xdg-open htmlcov/index.html
```

État actuel :

- 31 tests
- 99% de couverture sur `app`

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## CI/CD et déploiement

### Intégration continue

Workflow : `/.github/workflows/ci.yml`

Fonctionnement :

- déclenché sur `push` vers toutes les branches ;
- déclenché sur `pull_request` vers `main` et `develop` ;
- installe Python 3.11 ;
- installe les dépendances ;
- lance Pytest avec couverture minimale ;
- génère `coverage.xml` et `htmlcov/`.

### Déploiement continu

Workflow : `/.github/workflows/deploy-hf.yml`

Fonctionnement :

- déclenché sur `push` vers `main` ;
- déclenchable manuellement avec `workflow_dispatch` ;
- synchronise le dépôt vers Hugging Face Spaces.

### Secret GitHub utilisé

```text
HF_TOKEN
```

### Déploiement Hugging Face

- application : [mxmbrbr-futurisys-ml-api.hf.space](https://mxmbrbr-futurisys-ml-api.hf.space)
- Swagger : [mxmbrbr-futurisys-ml-api.hf.space/docs](https://mxmbrbr-futurisys-ml-api.hf.space/docs)
- health check : [mxmbrbr-futurisys-ml-api.hf.space/health](https://mxmbrbr-futurisys-ml-api.hf.space/health)

### Comportement sur Hugging Face

Le Space peut fonctionner sans PostgreSQL disponible. Dans ce cas :

- `/predict` continue de retourner une prédiction ;
- la persistance dans `prediction_inputs` et `prediction_outputs` est ignorée ;
- la traçabilité complète reste réservée à l'exécution locale ou à un déploiement avec une base PostgreSQL accessible.

### Limite actuelle avec PostgreSQL distant

Même avec une base distante fonctionnelle, la liaison entre le Space Hugging
Face et PostgreSQL n'est pas garantie.

Dans le cadre de ce projet, PostgreSQL distant a été validé pour :

- l'API locale ;
- Docker en local.

En revanche, Hugging Face Spaces limite les sorties réseau aux ports `80`,
`443` et `8080`, tandis que les connexions PostgreSQL managées passent
généralement par `5432` ou `6543`. Cette contrainte peut empêcher la
persistance distante depuis le Space, même si la même `DATABASE_URL` fonctionne
parfaitement en local.

Dans ce cas, il est préférable de :

- conserver PostgreSQL pour les environnements local et Docker ;
- documenter clairement la limite de plateforme ;
- éviter de forcer un contournement complexe qui sortirait du périmètre du POC.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Traçabilité des prédictions

Le projet garantit une traçabilité locale des inférences :

- les données source sont stockées dans `employees` ;
- chaque payload reçu par `/predict` est stocké dans `prediction_inputs` ;
- chaque résultat retourné est stocké dans `prediction_outputs`.

Si `id_employee` est fourni dans le payload :

- l'API retrouve l'employe via son identifiant metier `employees.id_employee` ;
- puis la prediction est reliee a la ligne correspondante en base.

Sinon :

- l'API tente un matching exact avec les données déjà présentes en base.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Limites et améliorations

- PostgreSQL distant est validé pour l'API locale et Docker, mais pas garanti
  pour Hugging Face Spaces en raison des contraintes réseau de la plateforme.
- La sécurité repose sur une clé API simple, adaptée à un POC mais pas à une
  authentification complète de niveau production.
- Un endpoint `/predict/by-employee/{id_employee}` pourrait être ajouté plus tard.
- Le protocole de réentraînement du modèle peut encore être davantage automatisé.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Auteur

Maxime Barbier

Projet GitHub :
[https://github.com/maximebarbier01/futurisys-ml-api](https://github.com/maximebarbier01/futurisys-ml-api)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
