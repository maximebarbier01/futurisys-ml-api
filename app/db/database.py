import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


#************************
#* Chargement config    *
#************************

load_dotenv()


#************************
#* Lecture configuration *
#************************

def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is required.")

    return database_url


#************************
#* Objets SQLAlchemy    *
#************************

engine = create_engine(get_database_url())

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


#************************
#* Dependance FastAPI   *
#************************

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
