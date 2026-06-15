from app.db import models  # noqa: F401 (Module importé mais non utilisé)
                           # --> Charge tous les modèles SQLAlchemy pour que Base.metadata connaisse les tables à créer.
from app.db.database import Base, engine 


#************************
#* Creation des tables  *
#************************

def main():
    """
    Crée en base toutes les tables déclarées dans les modèles SQLAlchemy.
    """
    Base.metadata.create_all(bind=engine)     # Crée les tables connues par Base.metadata si elles n'existent pas déjà.
    print("Database tables created successfully.")


#************************
#* Point d'entree       *
#************************

if __name__ == "__main__":
    # Exécute main() uniquement si le script est lancé directement.
    main()
