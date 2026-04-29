from pathlib import Path
from typing import Any

import joblib
import pandas as pd


MODEL_PATH = Path(__file__).resolve().parents[2] / "model" / "final_model.joblib"


class ModelService:
    def __init__(self, model_path: Path = MODEL_PATH):
        self.model_path = model_path
        self.artifact = self._load_artifact()

        self.model = self.artifact["model"]
        self.threshold = float(self.artifact["threshold"])
        self.feature_columns = self.artifact["feature_columns"]

    def _load_artifact(self) -> dict[str, Any]:
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        return joblib.load(self.model_path)

    def predict_proba(self, input_data: dict) -> float:
        X = pd.DataFrame([input_data])
        X = X[self.feature_columns]
        proba = self.model.predict_proba(X)[:, 1][0]
        return float(proba)

    def predict(self, input_data: dict) -> dict:
        proba = self.predict_proba(input_data)
        prediction = int(proba >= self.threshold)

        return {
            "prediction": prediction,
            "probability": proba,
            "threshold": self.threshold,
            "label": "attrition" if prediction == 1 else "non_attrition",
        }


model_service = ModelService()