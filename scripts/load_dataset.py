import argparse # sert à créer un script exécutable depuis le terminal avec des arguments.
from pathlib import Path

import pandas as pd

from app.db.database import SessionLocal
from app.db.models import Employee


#************************
#* Colonnes attendues   *
#************************

# Colonnes obligatoires attendues dans le CSV.
EXPECTED_COLUMNS = [
    "id_employee",
    "age",
    "revenu_mensuel",
    "nombre_experiences_precedentes",
    "annee_experience_totale",
    "annees_dans_l_entreprise",
    "annees_dans_le_poste_actuel",
    "satisfaction_employee_environnement",
    "satisfaction_employee_nature_travail",
    "satisfaction_employee_equipe",
    "satisfaction_employee_equilibre_pro_perso",
    "note_evaluation_precedente",
    "note_evaluation_actuelle",
    "niveau_hierarchique_poste",
    "heure_supplementaires",
    "augementation_salaire_precedente",
    "nombre_participation_pee",
    "nb_formations_suivies",
    "distance_domicile_travail",
    "niveau_education",
    "annees_depuis_la_derniere_promotion",
    "annes_sous_responsable_actuel",
    "genre",
    "statut_marital",
    "departement",
    "poste",
    "domaine_etude",
    "frequence_deplacement",
]

INT_COLUMNS = [
    "id_employee",
    "age",
    "revenu_mensuel",
    "nombre_experiences_precedentes",
    "annee_experience_totale",
    "annees_dans_l_entreprise",
    "annees_dans_le_poste_actuel",
    "satisfaction_employee_environnement",
    "satisfaction_employee_nature_travail",
    "satisfaction_employee_equipe",
    "satisfaction_employee_equilibre_pro_perso",
    "note_evaluation_precedente",
    "note_evaluation_actuelle",
    "niveau_hierarchique_poste",
    "heure_supplementaires",
    "nombre_participation_pee",
    "nb_formations_suivies",
    "distance_domicile_travail",
    "niveau_education",
    "annees_depuis_la_derniere_promotion",
    "annes_sous_responsable_actuel",
]

FLOAT_COLUMNS = ["augementation_salaire_precedente"]

TEXT_COLUMNS = [
    "genre",
    "statut_marital",
    "departement",
    "poste",
    "domaine_etude",
    "frequence_deplacement",
]


#************************
#* Parsing CLI          *
#************************

def parse_args():
    """
    Définit et récupère les arguments CLI passés au script en ligne de commande.
    """

    parser = argparse.ArgumentParser(description="Importez l'ensemble de données RH dans PostgreSQL.")

    # Chemin du fichier CSV à importer.
    parser.add_argument(
        "--csv-path",
        required=True,
        help="Chemin d'accès au fichier CSV à importer.",
    )
    # Optionnel : permet de vider la table employees avant import.
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Supprimez les employés existants avant d'importer l'ensemble de données.",
    )
    return parser.parse_args()


#************************
#* Validation dataset   *
#************************

def validate_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Vérifie la structure du dataset, nettoie les champs et convertit les types.
    """
    missing_columns = [column for column in EXPECTED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Colonnes requises manquantes: {missing_columns}")

    # Garde uniquement les colonnes attendues, dans le bon ordre.
    dataset = df[EXPECTED_COLUMNS].copy()

    # Bloque l'import si des valeurs manquantes sont présentes.
    if dataset.isnull().any().any():
        null_columns = dataset.columns[dataset.isnull().any()].tolist()
        raise ValueError(f"Le dataset contient des valeurs nulles dans les colonnes : {null_columns}")

    for column in INT_COLUMNS:
        dataset[column] = dataset[column].astype(int)

    for column in FLOAT_COLUMNS:
        dataset[column] = dataset[column].astype(float)

    for column in TEXT_COLUMNS:
        dataset[column] = dataset[column].astype(str).str.strip()

    return dataset


#************************
#* Import principal     *
#************************

def main():
    """
    Lit le CSV, valide les données et les insère dans la table employees.
    """
    # Récupération des arguments CLI.
    args = parse_args() 
    csv_path = Path(args.csv_path)
 
    # Vérifie que le fichier CSV existe.
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {csv_path}")

    # Lecture et validation du dataset.
    dataframe = pd.read_csv(csv_path)
    dataset = validate_dataset(dataframe)

    # Conversion du DataFrame en liste de dictionnaires.
    records = dataset.to_dict(orient="records")


    # Ouverture d'une session avec la base de données.
    db = SessionLocal()
    try:
        # Si demandé, suppression des salariés déjà présents.
        if args.truncate:
            db.query(Employee).delete()
            db.commit()

        # Création des objets SQLAlchemy à partir des lignes du CSV.
        employees = [Employee(**record) for record in records]

            # Insertion en masse des salariés.
        db.bulk_save_objects(employees) 
        db.commit()
        print(f"Import de {len(records)} employés dans PostgreSQL.")
    finally:
        db.close()


#************************
#* Point d'entree       *
#************************

if __name__ == "__main__":
    main()
