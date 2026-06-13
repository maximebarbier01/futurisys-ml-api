import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


#************************
#* Chargement config    *
#************************

# Charge les variables d'environnement définies dans le fichier .env.
load_dotenv()
# Grâce à load_dotenv(), la variable DATABASE_URL devient accessible avec os.getenv("DATABASE_URL").

#************************
#* Lecture configuration *
#************************

def get_database_url() -> str:
    """
    Récupère l'URL de connexion à la base de données.

    Retour
    ------
    str
        URL de connexion utilisée par SQLAlchemy.

    Erreur
    ------
    RuntimeError
        Levée si la variable DATABASE_URL n'est pas définie.
    """
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("La variable d'environnement DATABASE_URL est requise.")

    return database_url


#************************
#* Objets SQLAlchemy    *
#************************

# Création de l'engine SQLAlchemy (objet bas niveau qui gère la connexion avec la base de données)
engine = create_engine(get_database_url())

# Création d'une fabrique de sessions SQLAlchemy (permet de créer une nouvelle session à chaque requête)
SessionLocal = sessionmaker(
    autocommit=False, # Les transactions ne sont pas validées automatiquement.
    autoflush=False,  # Les changements ne sont pas envoyés automatiquement avant chaque requête.
    bind=engine,      # Les sessions créées utiliseront l'engine défini ci-dessus.
)

# Base est la classe parente de tous les modèles SQLAlchemy.
Base = declarative_base()
#? SQLAlchemy utilise cette Base pour connaître la structure des tables.

#************************
#* Dependance FastAPI   *
#************************

def get_db():
    """
    Fournit une session de base de données à FastAPI.

    Cette fonction est utilisée comme dépendance dans les endpoints.

    Exemple :
    def predict(input_data: PredictionInput, db: Session = Depends(get_db)):
        ...

    Fonctionnement :
    1. Une session SQLAlchemy est ouverte.
    2. Elle est fournie temporairement à l'endpoint avec yield.
    3. Une fois la requête terminée, la session est fermée proprement.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
