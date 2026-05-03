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

Ce projet est un Proof of Concept réalisé dans le cadre du parcours OpenClassrooms.

L'objectif est de déployer un modèle de machine learning issu du projet **"Classifier automatiquement des informations"** afin de le rendre exploitable via une API.

Le projet répond à une demande de Futurisys, entreprise souhaitant rendre ses modèles de machine learning opérationnels, testables et accessibles à travers une API performante.

L'API permet de prédire le risque d'attrition d'un collaborateur à partir de données RH, en s'appuyant sur un modèle entraîné précédemment et exposé via **FastAPI**.

Le projet met également en place des bonnes pratiques d'ingénierie logicielle :

- structuration claire du dépôt ;
- gestion des dépendances avec Poetry ;
- tests automatisés avec Pytest ;
- intégration continue avec GitHub Actions ;
- déploiement continu vers Hugging Face Spaces ;
- documentation d'installation, d'utilisation et de déploiement.

---

## Stack technique

- Python 3.11
- WSL2 Ubuntu 24.04 LTS
- Conda
- Poetry
- FastAPI
- Pydantic
- Pytest
- Pytest-cov
- Scikit-learn
- LightGBM
- Imbalanced-learn
- Joblib
- Docker
- Git / GitHub
- GitHub Actions
- Hugging Face Spaces
- PostgreSQL, prévu pour la persistance des prédictions

---

## Structure du projet

```text
futurisys-ml-api/
├── app/
│   ├── api/
│   │   └── routes.py
│   ├── core/
│   ├── db/
│   ├── schemas/
│   │   └── prediction.py
│   ├── services/
│   │   └── model_service.py
│   └── main.py
├── docs/
├── model/
│   └── final_model.joblib
├── notebooks/
├── scripts/
├── sql/
├── tests/
│   ├── conftest.py
│   └── test_api.py
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy-hf.yml
├── Dockerfile
├── README.md
├── pyproject.toml
├── poetry.lock
├── requirements.txt
└── requirements-dev.txt
```

---

## Modèle de machine learning

Le modèle utilisé dans ce projet provient du projet OpenClassrooms précédent consacré à la classification automatique.

Le modèle final est sauvegardé sous forme d'artefact Joblib :

```text
model/final_model.joblib
```

Cet artefact contient :

- le pipeline de prédiction complet ;
- le seuil de décision métier ;
- la liste des variables attendues en entrée ;
- des métadonnées de traçabilité du modèle.

L'API ne réentraîne pas le modèle. Elle charge l'artefact existant au démarrage, reçoit des données au format JSON, les transforme en DataFrame pandas, puis renvoie une prédiction.

---

## Installation locale

### 1. Cloner le dépôt

```bash
git clone git@github.com:maximebarbier01/futurisys-ml-api.git
cd futurisys-ml-api
```

### 2. Créer l'environnement Conda

```bash
conda create -n futurisys-ml-api python=3.11 -y
conda activate futurisys-ml-api
```

### 3. Installer les dépendances avec Poetry

```bash
poetry env use $(which python)
poetry install
```

### 4. Générer les fichiers requirements si nécessaire

Pour les dépendances de production :

```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

Pour les dépendances de développement et de test :

```bash
poetry export --with dev -f requirements.txt --output requirements-dev.txt --without-hashes
```

---

## Lancer l'API en local

```bash
uvicorn app.main:app --reload
```

L'API est alors disponible à l'adresse suivante :

```text
http://127.0.0.1:8000
```

Documentation Swagger locale :

```text
http://127.0.0.1:8000/docs
```

Endpoint de vérification :

```text
http://127.0.0.1:8000/health
```

---

## API déployée

L'API est déployée sur Hugging Face Spaces via Docker.

- URL de l'application : https://mxmbrbr-futurisys-ml-api.hf.space
- Documentation Swagger : https://mxmbrbr-futurisys-ml-api.hf.space/docs
- Health check : https://mxmbrbr-futurisys-ml-api.hf.space/health

Le déploiement est automatisé avec GitHub Actions. Lorsqu'une Pull Request est fusionnée dans la branche `main`, le workflow CD synchronise automatiquement le dépôt GitHub vers Hugging Face Spaces.

---

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
    "genre": "M",
    "statut_marital": "Marié(e)",
    "departement": "Consulting",
    "poste": "Consultant",
    "domaine_etude": "Transformation Digitale",
    "frequence_deplacement": "Occasionnel"
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

---

## Interprétation de la réponse

- `prediction = 1` : le modèle prédit un risque d'attrition.
- `prediction = 0` : le modèle prédit une absence d'attrition.
- `probability` : probabilité estimée d'attrition.
- `threshold` : seuil de décision retenu lors de l'entraînement.
- `label` : libellé lisible de la prédiction.

---

## Endpoints disponibles

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Vérifie que l'API est accessible |
| `GET` | `/health` | Vérifie l'état de santé de l'API |
| `POST` | `/predict` | Retourne une prédiction d'attrition |

---

## Lancer les tests

Lancer l'ensemble des tests :

```bash
pytest
```

Lancer les tests avec couverture :

```bash
pytest --cov=app --cov-report=term-missing tests/
```

Le pipeline CI impose également un seuil minimal de couverture.

---

## Environnements

Le projet distingue trois environnements.

### Développement local

L'environnement local repose sur WSL2 Ubuntu, Conda et Poetry.

Il permet de :

- développer l'API ;
- tester localement les endpoints ;
- lancer les tests unitaires ;
- vérifier le comportement du modèle avant intégration.

### Test / intégration continue

L'environnement de test est géré par GitHub Actions.

À chaque push ou Pull Request, le workflow CI :

- installe Python 3.11 ;
- installe les dépendances depuis `requirements-dev.txt` ;
- exécute les tests Pytest ;
- calcule la couverture de code ;
- bloque l'intégration si les tests échouent.

### Production

L'environnement de production est hébergé sur Hugging Face Spaces.

L'application est :

- construite via Docker ;
- exposée sur le port `7860` ;
- accessible publiquement sous forme d'API FastAPI.

---

## CI/CD

Le projet utilise deux workflows GitHub Actions.

### Intégration continue

Fichier :

```text
.github/workflows/ci.yml
```

Rôle :

- exécuter les tests automatiquement ;
- vérifier la couverture de code ;
- empêcher l'intégration de code non valide.

Déclenchement :

- push sur `main`, `develop` ou `feature/*` ;
- Pull Request vers `main` ou `develop`.

### Déploiement continu

Fichier :

```text
.github/workflows/deploy-hf.yml
```

Rôle :

- synchroniser le dépôt GitHub avec Hugging Face Spaces ;
- déclencher automatiquement le rebuild Docker du Space ;
- publier la dernière version stable de l'API.

Déclenchement :

- push sur `main` ;
- exécution manuelle possible via `workflow_dispatch`.

---

## Protection de la branche principale

La branche `main` est protégée afin de garantir la stabilité de la version principale du projet.

Les règles mises en place sont les suivantes :

- toute modification doit passer par une Pull Request ;
- le job GitHub Actions `test` doit réussir avant fusion ;
- la branche de travail doit être à jour avec `main` avant le merge.

Cette configuration empêche l'intégration d'un code qui ne passe pas les tests automatiques.

---

## Workflow Git

Le projet suit une organisation simple des branches :

- `main` : branche stable, utilisée pour le déploiement ;
- `feature/*` : nouvelles fonctionnalités ;
- `fix/*` : corrections ;
- `docs/*` : documentation.

Exemples :

```bash
git checkout -b feature/api-fastapi
git checkout -b fix/hf-lightgbm-runtime
git checkout -b docs/update-readme
```

Les commits suivent une convention descriptive :

```text
feat: ajout d'une fonctionnalité
fix: correction d'un bug
docs: modification de la documentation
test: ajout ou modification de tests
ci: modification de la configuration CI/CD
chore: tâche technique ou maintenance
```

---

## Docker

Le déploiement Hugging Face Spaces repose sur Docker.

Le `Dockerfile` :

- utilise Python 3.11 ;
- installe les dépendances système nécessaires à LightGBM ;
- installe les dépendances Python depuis `requirements.txt`;
- lance l'API avec Uvicorn sur le port `7860`.

Commande équivalente exécutée dans le container :

```bash
uvicorn app.main:app --host 0.0.0.0 --port 7860
```

---

## Gestion des secrets

Le déploiement vers Hugging Face utilise un token stocké dans les secrets GitHub Actions.

Secret utilisé :

```text
HF_TOKEN
```

Ce token n'est pas versionné dans le dépôt. Il est uniquement utilisé par GitHub Actions pour synchroniser le dépôt vers Hugging Face Spaces.

---

## Base de données PostgreSQL

Une base PostgreSQL est prévue pour stocker les prédictions et historiser les appels au modèle.

Les éléments liés à la base sont organisés dans :

```text
app/db/
sql/
scripts/
```

Cette partie permet de préparer l'extension du POC vers une architecture plus complète avec persistance des entrées, sorties et métadonnées de prédiction.

---

## Statut du projet

Fonctionnalités déjà mises en place :

- API FastAPI fonctionnelle ;
- modèle ML chargé depuis un artefact Joblib ;
- endpoint `/predict` opérationnel ;
- documentation Swagger générée automatiquement ;
- tests Pytest ;
- couverture de code ;
- pipeline CI avec GitHub Actions ;
- déploiement Docker sur Hugging Face Spaces ;
- pipeline CD automatisé ;
- protection de la branche `main`.

---