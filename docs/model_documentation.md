# Documentation technique du modèle

## 1. Objectif métier

Le modèle a pour objectif de prédire le risque d’attrition d’un collaborateur à partir de variables RH.

Cette prédiction permet :
- d’identifier les profils à risque
- de faciliter l’analyse RH
- de rendre le modèle exploitable via une API

## 2. Type de problème

Le problème traité est un problème de classification binaire.

Sorties attendues :
- `0` : `non_attrition`
- `1` : `attrition`

L’API retourne également une probabilité associée à la classe positive ainsi que le seuil de décision utilisé.

## 3. Intégration dans le projet

Le modèle est exposé via une API FastAPI.

Flux de fonctionnement :
1. le client envoie un payload JSON à l’endpoint `/predict`
2. le payload est validé par Pydantic
3. les données sont transmises au service modèle
4. le modèle calcule une probabilité
5. la probabilité est comparée à un seuil métier
6. l’API retourne la classe prédite, la probabilité, le seuil et le label
7. les inputs et outputs sont enregistrés en base PostgreSQL en local

## 4. Artefact du modèle

Le modèle déployé est chargé depuis l’artefact suivant :

```text
model/final_model.joblib
```

Cet artefact contient :
- le pipeline de prédiction
- le seuil de décision métier
- la liste des variables attendues en entrée
- les métadonnées utiles au chargement du modèle

L’API ne réentraîne pas le modèle. Elle charge uniquement l’artefact déjà entraîné au démarrage.

## 5. Variables d’entrée

Le modèle attend les variables suivantes :

- `age`
- `revenu_mensuel`
- `nombre_experiences_precedentes`
- `annee_experience_totale`
- `annees_dans_l_entreprise`
- `annees_dans_le_poste_actuel`
- `satisfaction_employee_environnement`
- `satisfaction_employee_nature_travail`
- `satisfaction_employee_equipe`
- `satisfaction_employee_equilibre_pro_perso`
- `note_evaluation_precedente`
- `note_evaluation_actuelle`
- `niveau_hierarchique_poste`
- `heure_supplementaires`
- `augementation_salaire_precedente`
- `nombre_participation_pee`
- `nb_formations_suivies`
- `distance_domicile_travail`
- `niveau_education`
- `annees_depuis_la_derniere_promotion`
- `annes_sous_responsable_actuel`
- `genre`
- `statut_marital`
- `departement`
- `poste`
- `domaine_etude`
- `frequence_deplacement`

## 6. Validation des données

La validation des données d’entrée est assurée par Pydantic dans l’API.

Les contrôles portent sur :
- la présence des champs obligatoires
- les types
- les bornes numériques
- les catégories autorisées pour certaines variables
- la cohérence du format attendu par le modèle

Exemples d’erreurs gérées :
- champ manquant
- type invalide
- valeur hors bornes
- catégorie inconnue

## 7. Sortie du modèle

L’API retourne une réponse de la forme :

```json
{
  "prediction": 1,
  "probability": 0.73,
  "threshold": 0.211717,
  "label": "attrition"
}
```

Description des champs :
- `prediction` : classe finale retournée par le modèle
- `probability` : probabilité de la classe positive
- `threshold` : seuil de décision appliqué
- `label` : libellé métier associé à la prédiction

## 8. Seuil de décision

Le modèle ne se limite pas à retourner une probabilité.  
Cette probabilité est comparée à un seuil métier stocké dans l’artefact du modèle.

Règle utilisée :
- si `probability < threshold`, alors `prediction = 0`
- si `probability >= threshold`, alors `prediction = 1`

Le seuil n’a pas été fixé arbitrairement à `0.5`.  
Il a été choisi à partir d’une optimisation via la **precision-recall curve**, afin d’obtenir un compromis plus pertinent pour le besoin métier.

Ce choix permet d’adapter la décision aux enjeux RH du projet, en privilégiant la détection des collaborateurs à risque plutôt qu’une simple règle statistique standard.

## 9. Performance du modèle

Le modèle final retenu est un **LightGBM** entraîné sur les variables initiales nettoyées.

Ses performances observées sur le jeu de test sont les suivantes :
- Precision : 0,53
- Recall : 0,85
- F1-score : 0,65
- Average precision : 0,70

La métrique d’optimisation utilisée lors de la sélection du modèle était l’**average precision**.

Ce choix est cohérent avec le contexte du projet, car la classe positive (`départ`) est minoritaire
(237 départs sur 1 470 salariés, soit environ 16 %), et l’objectif métier est de bien classer les salariés
par niveau de risque afin de faire remonter un maximum de vrais départs en haut du score.

L’average precision est donc plus pertinente que l’accuracy dans ce contexte :
elle évalue la qualité du **ranking des profils à risque**, là où l’accuracy pourrait paraître bonne
tout en ratant trop de départs réels.

Le seuil de décision final a été fixé à **0,2117**, à partir des probabilités issues de la validation croisée
sur le jeu d’entraînement, plus précisément à partir des probabilités **out-of-fold**.

Cette méthode permet :
- de privilégier la détection de la classe minoritaire ;
- d’éviter d’ajuster le seuil directement sur le jeu de test ;
- d’obtenir un compromis opérationnel entre précision et rappel.

L’objectif n’était donc pas seulement d’obtenir un bon score global, mais de produire un modèle capable
de détecter la majorité des départs réellement à risque tout en conservant des alertes cohérentes
pour les équipes RH.

## 10. Compromis métier entre faux positifs et faux négatifs

Le coût métier principal est le **faux négatif** : un salarié qui quitte l’entreprise sans avoir été identifié comme à risque.

Dans ce contexte, le choix de modélisation privilégie la **détection d’un maximum de départs réels**, quitte à accepter davantage de faux positifs.

Ces faux positifs restent souvent **plausibles d’un point de vue métier** :
- ils correspondent fréquemment à des profils fragiles ;
- ils ne se traduisent pas nécessairement par un départ à court terme ;
- mais ils constituent malgré tout un signal de vigilance utile pour les équipes RH.

Le modèle doit donc être utilisé comme un **outil de priorisation du risque**, et non comme un système de décision automatique.

## 11. Usage recommandé du modèle

Le modèle doit être utilisé comme un outil d’aide à la priorisation.

Ce qu’il apporte :
- une vue consolidée du risque d’attrition ;
- une capacité à détecter la majorité des départs ;
- des alertes cohérentes avec les signaux RH observés.

Ce qu’il ne garantit pas :
- prédire tous les départs ;
- distinguer parfaitement tous les vrais risques ;
- capturer les facteurs absents des données disponibles.

Usage recommandé :
- utiliser le score comme un outil d’aide à la priorisation ;
- le combiner avec l’expertise RH et managériale ;
- ne jamais en faire un outil de décision automatique.

## 12. Tests associés au modèle

Le comportement du modèle est couvert par plusieurs niveaux de tests :

- `tests/test_model_service.py`
  Vérifie le chargement de l’artefact, le calcul des probabilités et la logique de seuil.

- `tests/test_api.py`
  Vérifie le bon fonctionnement de l’endpoint `/predict`, les cas nominaux, les erreurs de validation et les cas fonctionnels réalistes.

- `tests/test_repository.py`
  Vérifie la persistance des inputs et outputs liés aux prédictions.

- `tests/test_database.py`
  Vérifie le cycle de vie des sessions de base de données.

## 13. Maintenance du modèle

Un protocole de maintenance recommandé est le suivant :

1. mettre à jour le dataset source
2. relancer la préparation des données
3. réentraîner le modèle
4. recalculer les métriques de performance
5. réévaluer le seuil métier
6. exporter un nouvel artefact `final_model.joblib`
7. relancer les tests unitaires et fonctionnels
8. redéployer l’API

Ce protocole permet de garantir :
- la stabilité du service
- la reproductibilité des résultats
- la cohérence entre le modèle et l’API

## 14. Limites du modèle

Les principales limites identifiées sont :
- la performance du modèle dépend de la qualité des données RH
- une dérive des données peut dégrader les performances dans le temps
- les prédictions doivent être utilisées comme aide à la décision
- le déploiement Hugging Face ne garantit pas une traçabilité PostgreSQL complète sans base accessible

## 15. Perspectives d’amélioration

Des évolutions possibles sont :
- automatiser davantage le protocole de réentraînement
- ajouter un suivi de dérive des données
- historiser les versions du modèle plus finement
- exposer un endpoint dédié du type `/predict/by-employee/{employee_id}`
- intégrer un monitoring plus avancé en production
