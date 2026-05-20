from app.db import models  # noqa: F401
from app.db.database import Base, engine


#************************
#* Creation des tables  *
#************************

def main():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


#************************
#* Point d'entree       *
#************************

if __name__ == "__main__":
    main()
