from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base


#************************
#* Utilitaire dates     *
#************************


def utc_now() -> datetime:
    """
    Retourne la date et l'heure actuelles en UTC.

    Cette fonction est utilisée comme valeur par défaut
    pour les colonnes created_at.
    """
    return datetime.now(UTC)


#************************
#* Table employees      *
#************************

class Employee(Base):
    """
    Modèle SQLAlchemy représentant la table employees.
    """

    # Nom réel de la table dans la base de données.
    __tablename__ = "employees"

    # Identifiant technique du salarié.
    id = Column(Integer, primary_key=True, index=True)
    id_employee = Column(Integer, unique=True, nullable=False, index=True)

    # Identifiant métier du salarié 
    id_employee = Column(Integer, unique=True, nullable=False, index=True)

    age = Column(Integer, nullable=False)
    revenu_mensuel = Column(Integer, nullable=False)
    nombre_experiences_precedentes = Column(Integer, nullable=False)
    annee_experience_totale = Column(Integer, nullable=False)
    annees_dans_l_entreprise = Column(Integer, nullable=False)
    annees_dans_le_poste_actuel = Column(Integer, nullable=False)

    satisfaction_employee_environnement = Column(Integer, nullable=False)
    satisfaction_employee_nature_travail = Column(Integer, nullable=False)
    satisfaction_employee_equipe = Column(Integer, nullable=False)
    satisfaction_employee_equilibre_pro_perso = Column(Integer, nullable=False)

    note_evaluation_precedente = Column(Integer, nullable=False)
    note_evaluation_actuelle = Column(Integer, nullable=False)

    niveau_hierarchique_poste = Column(Integer, nullable=False)
    heure_supplementaires = Column(Integer, nullable=False)
    augementation_salaire_precedente = Column(Float, nullable=False)
    nombre_participation_pee = Column(Integer, nullable=False)
    nb_formations_suivies = Column(Integer, nullable=False)
    distance_domicile_travail = Column(Integer, nullable=False)
    niveau_education = Column(Integer, nullable=False)
    annees_depuis_la_derniere_promotion = Column(Integer, nullable=False)
    annes_sous_responsable_actuel = Column(Integer, nullable=False)

    genre = Column(String(10), nullable=False)
    statut_marital = Column(String(50), nullable=False)
    departement = Column(String(100), nullable=False)
    poste = Column(String(100), nullable=False)
    domaine_etude = Column(String(100), nullable=False)
    frequence_deplacement = Column(String(50), nullable=False)

    # Date de création de la ligne en base.
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relation entre Employee et PredictionInputLog.
    prediction_inputs = relationship("PredictionInputLog", back_populates="employee")
    # back_populates="employee" fait le lien avec l'attribut employee défini dans la classe PredictionInputLog.


#**********************************
#* Table prediction_inputs        *
#**********************************

class PredictionInputLog(Base):
    """
    Modèle SQLAlchemy représentant la table prediction_inputs.

    Cette table sert à historiser les données envoyées à l'endpoint /predict.
    """
    # Nom réel de la table dans la base de données.
    __tablename__ = "prediction_inputs"

    # Identifiant technique de l'input de prédiction.
    id = Column(Integer, primary_key=True, index=True)

    # Identifiant du salarié associé à la prédiction.
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)

    age = Column(Integer, nullable=False)
    revenu_mensuel = Column(Integer, nullable=False)
    nombre_experiences_precedentes = Column(Integer, nullable=False)
    annee_experience_totale = Column(Integer, nullable=False)
    annees_dans_l_entreprise = Column(Integer, nullable=False)
    annees_dans_le_poste_actuel = Column(Integer, nullable=False)

    satisfaction_employee_environnement = Column(Integer, nullable=False)
    satisfaction_employee_nature_travail = Column(Integer, nullable=False)
    satisfaction_employee_equipe = Column(Integer, nullable=False)
    satisfaction_employee_equilibre_pro_perso = Column(Integer, nullable=False)

    note_evaluation_precedente = Column(Integer, nullable=False)
    note_evaluation_actuelle = Column(Integer, nullable=False)

    niveau_hierarchique_poste = Column(Integer, nullable=False)
    heure_supplementaires = Column(Integer, nullable=False)
    augementation_salaire_precedente = Column(Float, nullable=False)
    nombre_participation_pee = Column(Integer, nullable=False)
    nb_formations_suivies = Column(Integer, nullable=False)
    distance_domicile_travail = Column(Integer, nullable=False)
    niveau_education = Column(Integer, nullable=False)
    annees_depuis_la_derniere_promotion = Column(Integer, nullable=False)
    annes_sous_responsable_actuel = Column(Integer, nullable=False)

    genre = Column(String(10), nullable=False)
    statut_marital = Column(String(50), nullable=False)
    departement = Column(String(100), nullable=False)
    poste = Column(String(100), nullable=False)
    domaine_etude = Column(String(100), nullable=False)
    frequence_deplacement = Column(String(50), nullable=False)

    # Date de création du log d'entrée.
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    #? -------------------------
    #? Relations SQLAlchemy
    #? -------------------------

    # Relation avec la table employee
    employee = relationship("Employee", back_populates="prediction_inputs")

    # Relation avec la table prediction_outputs 
    prediction_output = relationship(
        "PredictionOutputLog",
        back_populates="prediction_input",
        uselist=False, # Relation 1 -> 1
    )


#***********************************
#* Table prediction_outputs        *
#***********************************

class PredictionOutputLog(Base):
    """
    Modèle SQLAlchemy représentant la table prediction_outputs.

    Cette table sert à historiser les résultats produits par le modèle ML.
    """

    # Nom réel de la table dans la base de données.
    __tablename__ = "prediction_outputs"

    # Identifiant technique de la sortie de prédiction.
    id = Column(Integer, primary_key=True, index=True)
    prediction_input_id = Column(
        Integer,
        ForeignKey("prediction_inputs.id"),
        nullable=False,
        unique=True,     # garantit qu'un même input ne peut avoir qu'une seule sortie.
                         # C'est ce qui matérialise la relation 1 → 1 entre : PredictionInputLog et PredictionOutputLog.
    )

    prediction = Column(Integer, nullable=False)
    probability = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    label = Column(String(50), nullable=False)

    model_name = Column(String(100), nullable=True)
    model_version = Column(String(50), nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    prediction_input = relationship(
        "PredictionInputLog",
        back_populates="prediction_output",
    )
