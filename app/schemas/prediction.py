from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


PREDICTION_INPUT_EXAMPLE = {
    "age": 38,
    "revenu_mensuel": 5400,
    "nombre_experiences_precedentes": 3,
    "annee_experience_totale": 12,
    "annees_dans_l_entreprise": 4,
    "annees_dans_le_poste_actuel": 2,
    "satisfaction_employee_environnement": 3,
    "satisfaction_employee_nature_travail": 4,
    "satisfaction_employee_equipe": 4,
    "satisfaction_employee_equilibre_pro_perso": 3,
    "note_evaluation_precedente": 3,
    "note_evaluation_actuelle": 4,
    "niveau_hierarchique_poste": 2,
    "heure_supplementaires": 1,
    "augementation_salaire_precedente": 0.14,
    "nombre_participation_pee": 1,
    "nb_formations_suivies": 3,
    "distance_domicile_travail": 12,
    "niveau_education": 4,
    "annees_depuis_la_derniere_promotion": 1,
    "annes_sous_responsable_actuel": 2,
    "genre": "M",
    "statut_marital": "Marié(e)",
    "departement": "Consulting",
    "poste": "Consultant",
    "domaine_etude": "Transformation Digitale",
    "frequence_deplacement": "Occasionnel",
}


class PredictionInput(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": PREDICTION_INPUT_EXAMPLE})

    age: int = Field(..., ge=18, le=70)
    revenu_mensuel: int = Field(..., ge=0, le=50000)
    nombre_experiences_precedentes: int = Field(..., ge=0, le=20)
    annee_experience_totale: int = Field(..., ge=0, le=50)
    annees_dans_l_entreprise: int = Field(..., ge=0, le=50)
    annees_dans_le_poste_actuel: int = Field(..., ge=0, le=30)

    satisfaction_employee_environnement: int = Field(..., ge=1, le=4)
    satisfaction_employee_nature_travail: int = Field(..., ge=1, le=4)
    satisfaction_employee_equipe: int = Field(..., ge=1, le=4)
    satisfaction_employee_equilibre_pro_perso: int = Field(..., ge=1, le=4)

    note_evaluation_precedente: int = Field(..., ge=1, le=4)
    note_evaluation_actuelle: int = Field(..., ge=1, le=4)

    niveau_hierarchique_poste: int = Field(..., ge=1, le=5)
    heure_supplementaires: int = Field(..., ge=0, le=1)
    augementation_salaire_precedente: float = Field(..., ge=0.0, le=1.0)
    nombre_participation_pee: int = Field(..., ge=0, le=5)
    nb_formations_suivies: int = Field(..., ge=0, le=10)
    distance_domicile_travail: int = Field(..., ge=0, le=100)
    niveau_education: int = Field(..., ge=1, le=8)
    annees_depuis_la_derniere_promotion: int = Field(..., ge=0, le=30)
    annes_sous_responsable_actuel: int = Field(..., ge=0, le=30)

    genre: Literal["F", "M"]

    statut_marital: Literal[
        "Célibataire",
        "Divorcé(e)",
        "Marié(e)",
    ]

    departement: Literal[
        "Commercial",
        "Consulting",
        "Ressources Humaines",
    ]

    poste: Literal[
        "Assistant de Direction",
        "Cadre Commercial",
        "Consultant",
        "Directeur Technique",
        "Manager",
        "Représentant Commercial",
        "Ressources Humaines",
        "Senior Manager",
        "Tech Lead",
    ]

    domaine_etude: Literal[
        "Autre",
        "Entrepreunariat",
        "Infra & Cloud",
        "Marketing",
        "Ressources Humaines",
        "Transformation Digitale",
    ]

    frequence_deplacement: Literal[
        "Aucun",
        "Frequent",
        "Occasionnel",
    ]


class PredictionOutput(BaseModel):
    prediction: Literal[0, 1]
    probability: float = Field(..., ge=0.0, le=1.0)
    threshold: float = Field(..., ge=0.0, le=1.0)
    label: Literal["attrition", "non_attrition"]
