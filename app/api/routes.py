import logging

from fastapi import (
    APIRouter, 
    Depends, # Permet d'injecter automatiquement des dépendances dans les routes
    HTTPException
)
from sqlalchemy.orm import Session # Représente une session de connexion à la base de données
from sqlalchemy.exc import SQLAlchemyError  # Permet d'intercepter les erreurs SQLAlchemy


from app.core.security import require_api_key
from app.db.database import get_db
from app.db.repository import (
    create_prediction_input,
    create_prediction_output,
    find_matching_employee,
    get_employee_by_business_id,
)
from app.schemas.prediction import (
    PREDICTION_OUTPUT_EXAMPLE,
    PredictionInput,
    PredictionOutput,
)
from app.services.model_service import model_service


#************************
#* Router et logs       *
#************************

#? Création du router FastAPI.
# La dépendance require_api_key est appliquée à toutes les routes de ce router.
# Donc avant d'accéder à /predict, l'utilisateur doit fournir une clé API valide.
router = APIRouter(dependencies=[Depends(require_api_key)]) 

# Création du logger pour tracer les événements ou erreurs liés à ce module.
logger = logging.getLogger(__name__)

#************************
#* Endpoint prediction  *
#************************

@router.post(
    "/predict",
    response_model=PredictionOutput, # La réponse doit respecter le schéma PredictionOutput
    responses={
        200: {
            "content": {
                "application/json": {
                    # Exemple de réponse affiché dans la documentation Swagger / OpenAPI
                    "example": PREDICTION_OUTPUT_EXAMPLE,
                }
            }
        }
    },
)
def predict(input_data: PredictionInput, db: Session = Depends(get_db)):
    """
    Endpoint POST /predict

    Flux global :
    1. Vérification de l'API key
    2. Validation du JSON avec PredictionInput
    3. Conversion en dictionnaire Python
    4. Retrait éventuel de id_employee
    5. Prédiction ML avec model_service.predict()
    6. Recherche du salarié en base
    7. Enregistrement de l'input de prédiction
    8. Enregistrement de l'output de prédiction
    9. Retour de la prédiction
    """

    # ---------------------------------------------------------
    # 1) Vérification de l'API key
    # ---------------------------------------------------------
    # Cette étape est gérée automatiquement par le router :
    # router = APIRouter(dependencies=[Depends(require_api_key)])
    #
    # Si la clé API est absente ou invalide, FastAPI bloque la requête
    # avant même d'entrer dans cette fonction.

    # ---------------------------------------------------------
    # 2) Validation du JSON avec PredictionInput
    # ---------------------------------------------------------
    # Cette étape est aussi gérée automatiquement par FastAPI.
    # Le JSON envoyé par l'utilisateur est validé avec le schéma Pydantic PredictionInput.
    #
    # Si un champ obligatoire est absent ou invalide, FastAPI renvoie une erreur 422.
    #
    # Si la validation est correcte, FastAPI crée l'objet input_data.

    # ---------------------------------------------------------
    # 3) Conversion en dictionnaire Python
    # ---------------------------------------------------------
    # input_data est un objet Pydantic.
    # model_dump() le transforme en dictionnaire Python exploitable par le modèle ML.
    #
    # exclude_none=True permet de supprimer les champs dont la valeur est None.
    payload = input_data.model_dump(exclude_none=True)

    # ---------------------------------------------------------
    # 4) Retrait éventuel de id_employee
    # ---------------------------------------------------------
    # id_employee sert à retrouver un salarié via son identifiant métier.
    # En revanche, ce n'est pas une variable explicative du modèle ML.
    #
    # pop() récupère id_employee et le retire du dictionnaire payload.
    # Si id_employee n'existe pas, la valeur None est utilisée.
    id_employee = payload.pop("id_employee", None)

    # ---------------------------------------------------------
    # 5) Prédiction ML avec model_service.predict()
    # ---------------------------------------------------------
    # Le modèle reçoit uniquement les variables métier présentes dans payload.
    #
    # Exemple :
    # {
    #     "age": 38,
    #     "departement": "Consulting",
    #     "revenu_mensuel": 4200
    # }
    #
    # prediction_result contient la prédiction finale retournée par le modèle.
    prediction_result = model_service.predict(payload)

    try:
        # Variable qui contiendra le salarié retrouvé en base, si possible.
        employee = None

        # ---------------------------------------------------------
        # 6) Recherche du salarié en base
        # ---------------------------------------------------------

        if id_employee is not None:
            # Cas 1 :
            # L'utilisateur a fourni un id_employee.
            # On cherche donc explicitement ce salarié dans la base.
            employee = get_employee_by_business_id(db, id_employee)

            if employee is None:
                # Si aucun salarié ne correspond à cet id_employee,
                # on renvoie une erreur HTTP 404.
                raise HTTPException(
                    status_code=404,
                    detail=f"L'employé {id_employee} n'a pas été trouvé",
                )

        else:
            # Cas 2 :
            # Aucun id_employee n'a été fourni.
            # On essaie alors de retrouver un salarié correspondant
            # aux caractéristiques envoyées dans payload.
            #
            # Si aucun salarié n'est trouvé, ce n'est pas bloquant :
            # la prédiction pourra quand même être enregistrée sans identifiant métier.
            employee = find_matching_employee(db, payload)

        # ---------------------------------------------------------
        # 7) Enregistrement de l'input de prédiction
        # ---------------------------------------------------------
        # On sauvegarde en base les données utilisées pour faire la prédiction.
        #
        # Si un salarié a été retrouvé, on rattache l'input à son identifiant métier central.
        # Sinon, la clé étrangère reste à None.
        prediction_input = create_prediction_input(
            db,
            payload,
            id_employee=employee.id_employee if employee else None,
        )

        # ---------------------------------------------------------
        # 8) Enregistrement de l'output de prédiction
        # ---------------------------------------------------------
        # On sauvegarde ensuite le résultat de la prédiction.
        #
        # On stocke aussi le nom et la version du modèle utilisé,
        # ce qui permet de tracer les prédictions dans le temps.
        create_prediction_output(
            db=db,
            prediction_input_id=prediction_input.id,
            prediction_result=prediction_result,
            model_name=model_service.display_name,
            model_version=model_service.model_version,
        )

    except HTTPException:
        # Si une erreur HTTP a été levée volontairement,
        # par exemple un salarié introuvable en 404,
        # on la relance telle quelle.
        raise

    except SQLAlchemyError as exc:
        # Si une erreur SQLAlchemy survient pendant l'enregistrement en base,
        # on annule la transaction pour éviter de laisser la base dans un état incohérent.
        db.rollback()

        # On écrit un warning dans les logs.
        # La prédiction reste disponible, mais elle n'a pas pu être persistée en base.
        logger.warning(
            "Prediction tracking unavailable; returning prediction without persistence: %s",
            exc,
        )

    # ---------------------------------------------------------
    # 9) Retour de la prédiction
    # ---------------------------------------------------------
    # Même si le tracking en base échoue, l'utilisateur reçoit quand même
    # le résultat de la prédiction.
    return prediction_result
