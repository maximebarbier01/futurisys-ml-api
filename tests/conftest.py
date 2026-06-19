import os
from pathlib import Path
import sys

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool # force SQLAlchemy à réutiliser la même connexion pour toute la session de test.

# Racine du projet, utilisée pour permettre les imports depuis app/.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Variables d'environnement utilisées pendant les tests.
#! Elles doivent être définies avant l'import de l'application.
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("API_KEY", "test-api-key")
os.environ.setdefault("API_KEY_HEADER_NAME", "X-API-Key")

from app.db.database import get_db
from app.db.models import Base
from app.main import app


#********************************
#* Configuration environnement  *
#********************************

# Base SQLite en mémoire utilisée uniquement pour les tests.
TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    # Nécessaire avec FastAPI/TestClient, car SQLite limite sinon l'accès par thread.
    connect_args={"check_same_thread": False},
    # Permet de conserver la même connexion SQLite en mémoire pendant les tests.
    poolclass=StaticPool,
)

# Fabrique de sessions SQLAlchemy branchée sur la base de test.
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False, # évite que SQLAlchemy envoie automatiquement certaines modifications à la base avant certaines requêtes
    bind=engine,
)


#********************************
#* Fixtures de base de donnees  *
#********************************

@pytest.fixture(autouse=True)
def override_db():
    """
    Remplace la dépendance get_db de FastAPI par une session SQLite de test.

    Cette fixture est exécutée automatiquement pour chaque test.
    """

    # Crée les tables avant le test.
    Base.metadata.create_all(bind=engine)

    def _override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Force FastAPI à utiliser la base de test au lieu de la vraie base.
    app.dependency_overrides[get_db] = _override_get_db # garantit que les endpoints testés n’utilisent pas la vraie base PostgreSQL.

    yield

    # Nettoyage après le test.
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine) # garantit que chaque test repart d’une base propre.


@pytest.fixture
def db_session():
    """
    Fournit une session SQLAlchemy de test utilisable directement dans les tests.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
