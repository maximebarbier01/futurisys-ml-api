from sqlalchemy.orm import Session

from app.db.models import Employee, PredictionInputLog, PredictionOutputLog


#************************
#* Champs de matching   *
#************************

TRACKED_INPUT_FIELDS = (
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
)


#************************
#* Lecture employees    *
#************************

def get_employee_by_business_id(db: Session, id_employee: int) -> Employee | None:
    return db.query(Employee).filter_by(id_employee=id_employee).first()


def find_matching_employee(db: Session, input_data: dict) -> Employee | None:
    lookup = {field: input_data[field] for field in TRACKED_INPUT_FIELDS}
    return db.query(Employee).filter_by(**lookup).first()


#******************************
#* Ecriture prediction input  *
#******************************

def create_prediction_input(
    db: Session,
    input_data: dict,
    employee_id: int | None = None,
) -> PredictionInputLog:
    prediction_input = PredictionInputLog(employee_id=employee_id, **input_data)
    db.add(prediction_input)
    db.commit()
    db.refresh(prediction_input)
    return prediction_input


#*******************************
#* Ecriture prediction output  *
#*******************************

def create_prediction_output(
    db: Session,
    prediction_input_id: int,
    prediction_result: dict,
    model_name: str | None = None,
    model_version: str | None = None,
) -> PredictionOutputLog:
    prediction_output = PredictionOutputLog(
        prediction_input_id=prediction_input_id,
        prediction=prediction_result["prediction"],
        probability=prediction_result["probability"],
        threshold=prediction_result["threshold"],
        label=prediction_result["label"],
        model_name=model_name,
        model_version=model_version,
    )
    db.add(prediction_output)
    db.commit()
    db.refresh(prediction_output)
    return prediction_output
