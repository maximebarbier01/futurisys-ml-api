# Futurisys ML API

## Présentation

Ce projet est un Proof of Concept visant à déployer un modèle de machine learning issu du projet OpenClassrooms "Classifier automatiquement des informations".

L'objectif est de rendre le modèle accessible via une API FastAPI, avec une structure de code propre, des tests automatisés, une base PostgreSQL et une configuration CI/CD.

## Stack technique

- Python 3.12
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
conda create -n futurisys-ml-api python=3.12 -y
conda activate futurisys-ml-api
poetry env use python3.12
poetry install
```
