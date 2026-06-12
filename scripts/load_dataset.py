import argparse
from pathlib import Path

import pandas as pd

from app.db.database import SessionLocal
from app.db.models import Employee


#************************
#* Colonnes attendues   *
#************************

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
    parser = argparse.ArgumentParser(description="Load the HR dataset into PostgreSQL.")
    parser.add_argument(
        "--csv-path",
        required=True,
        help="Path to the CSV dataset to import.",
    )
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Delete existing employees before importing the dataset.",
    )
    return parser.parse_args()


#************************
#* Validation dataset   *
#************************

def validate_dataset(df: pd.DataFrame) -> pd.DataFrame:
    missing_columns = [column for column in EXPECTED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    dataset = df[EXPECTED_COLUMNS].copy()

    if dataset.isnull().any().any():
        null_columns = dataset.columns[dataset.isnull().any()].tolist()
        raise ValueError(f"Dataset contains null values in columns: {null_columns}")

    for column in INT_COLUMNS:
        dataset[column] = dataset[column].astype(int)

    for column in FLOAT_COLUMNS:
        dataset[column] = dataset[column].astype(float)

    for column in TEXT_COLUMNS:
        dataset[column] = dataset[column].astype(str).str.strip()

    if dataset["id_employee"].duplicated().any():
        duplicated_ids = dataset.loc[dataset["id_employee"].duplicated(), "id_employee"].tolist()
        raise ValueError(
            f"Dataset contains duplicate id_employee values: {duplicated_ids[:5]}"
        )

    return dataset


#************************
#* Import principal     *
#************************

def main():
    args = parse_args()
    csv_path = Path(args.csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {csv_path}")

    dataframe = pd.read_csv(csv_path)
    dataset = validate_dataset(dataframe)
    records = dataset.to_dict(orient="records")

    db = SessionLocal()
    try:
        if args.truncate:
            db.query(Employee).delete()
            db.commit()

        employees = [Employee(**record) for record in records]
        db.bulk_save_objects(employees)
        db.commit()
        print(f"Imported {len(records)} employees into PostgreSQL.")
    finally:
        db.close()


#************************
#* Point d'entree       *
#************************

if __name__ == "__main__":
    main()
