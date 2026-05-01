from pydantic import BaseModel, Field


class PredictionInput(BaseModel):
    age: int = Field(..., example=35)
    revenu_mensuel: int = Field(..., example=4200)
    nombre_experiences_precedentes: int = Field(..., example=2)
    annee_experience_totale: int = Field(..., example=10)
    annees_dans_l_entreprise: int = Field(..., example=5)
    annees_dans_le_poste_actuel: int = Field(..., example=3)

    satisfaction_employee_environnement: int = Field(..., example=3)
    satisfaction_employee_nature_travail: int = Field(..., example=4)
    satisfaction_employee_equipe: int = Field(..., example=3)
    satisfaction_employee_equilibre_pro_perso: int = Field(..., example=2)

    note_evaluation_precedente: int = Field(..., example=3)
    note_evaluation_actuelle: int = Field(..., example=4)

    niveau_hierarchique_poste: int = Field(..., example=2)
    heure_supplementaires: int = Field(..., json_schema_extra={"example": 0})
    augementation_salaire_precedente: int = Field(..., example=12)
    nombre_participation_pee: int = Field(..., example=1)
    nb_formations_suivies: int = Field(..., example=2)
    distance_domicile_travail: int = Field(..., example=8)
    niveau_education: int = Field(..., example=3)
    annees_depuis_la_derniere_promotion: int = Field(..., example=1)
    annes_sous_responsable_actuel: int = Field(..., example=3)

    genre: str = Field(..., example="Homme")
    statut_marital: str = Field(..., example="Marié")
    departement: str = Field(..., example="Recherche & Développement")
    poste: str = Field(..., example="Ingénieur de recherche")
    domaine_etude: str = Field(..., example="Sciences de la vie")
    frequence_deplacement: str = Field(..., example="Voyage rarement")


class PredictionOutput(BaseModel):
    prediction: int
    probability: float
    threshold: float
    label: str