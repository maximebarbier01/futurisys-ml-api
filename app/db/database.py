import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


#************************
#* Chargement config    *
#************************

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://futurisys_user:futurisys_password@localhost:5432/futurisys_ml_api",
)


#************************
#* Objets SQLAlchemy    *
#************************

engine = create_engine(DATABASE_URL)

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
