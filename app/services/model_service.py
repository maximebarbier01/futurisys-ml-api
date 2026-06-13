from pathlib import Path
from typing import Any

import joblib
import pandas as pd


#************************
#* Constante modele     *
#************************

MODEL_PATH = Path(__file__).resolve().parents[2] / "model" / "final_model.joblib"


#************************
#* Service de modele    *
#************************

class ModelService:
    def __init__(self, model_path: Path = MODEL_PATH):
        self.model_path = model_path
        self.artifact = self._load_artifact()

        self.model = self.artifact["model"]
        self.threshold = float(self.artifact["threshold"])
        self.feature_columns = self.artifact["feature_columns"]
        self.display_name = self.artifact.get("model_name", "final_model")
        self.model_version = str(self.artifact.get("model_version", "0.1.0"))

    def _load_artifact(self) -> dict[str, Any]:
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        return joblib.load(self.model_path)

    def predict_proba(self, input_data: dict) -> float:
        X = pd.DataFrame([input_data]) # dict transformé en DataFrame 
        X = X[self.feature_columns] # colonnes sont remises exactement dans l'ordre attendu par le modèle 
        proba = self.model.predict_proba(X)[:, 1][0] # le modèle calcule la probabilité de la classe positive
        return float(proba)

    def predict(self, input_data: dict) -> dict:
        proba = self.predict_proba(input_data)
        prediction = int(proba >= self.threshold)

        return {
            "prediction": prediction,
            "probability": proba,
            "threshold": self.threshold,
            "label": "risque_attrition_important" if prediction == 1 else "risque_attrition_faible",
        }


#************************
#* Instance partagee    *
#************************

model_service = ModelService()
