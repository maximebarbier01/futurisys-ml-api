from pathlib import Path

import numpy as np
import pytest

from app.services.model_service import ModelService


#********************************
#* Doubles de test             *
#********************************

class DummyModel:
    def __init__(self, proba: float = 0.73):
        self.proba = proba

    def predict_proba(self, X):
        return np.array([[1 - self.proba, self.proba]])


#********************************
#* Fabrique de service         *
#********************************

def build_service(monkeypatch, proba: float = 0.73, threshold: float = 0.5):
    artifact = {
        "model": DummyModel(proba=proba),
        "threshold": threshold,
        "feature_columns": ["age", "revenu_mensuel"],
        "model_name": "dummy_model",
        "model_version": "test",
    }
    monkeypatch.setattr(ModelService, "_load_artifact", lambda self: artifact)
    return ModelService(model_path=Path("dummy_model.joblib"))


#********************************
#* Tests chargement artefact   *
#********************************

def test_load_artifact_missing_file_raises(tmp_path):
    missing_model = tmp_path / "missing_model.joblib"

    with pytest.raises(FileNotFoundError):
        ModelService(model_path=missing_model)


#********************************
#* Tests predict_proba         *
#********************************

def test_predict_proba_returns_float(monkeypatch):
    service = build_service(monkeypatch, proba=0.73, threshold=0.5)

    payload = {
        "age": 38,
        "revenu_mensuel": 5400,
    }

    result = service.predict_proba(payload)

    assert isinstance(result, float)
    assert result == pytest.approx(0.73)


#********************************
#* Tests predict               *
#********************************

def test_predict_returns_expected_keys(monkeypatch):
    service = build_service(monkeypatch, proba=0.73, threshold=0.5)

    payload = {
        "age": 38,
        "revenu_mensuel": 5400,
    }

    result = service.predict(payload)

    assert set(result.keys()) == {"prediction", "probability", "threshold", "label"}


def test_predict_below_threshold_returns_low_attrition_risk(monkeypatch):
    service = build_service(monkeypatch, threshold=0.30)
    monkeypatch.setattr(service, "predict_proba", lambda _input: 0.29)

    result = service.predict({"age": 38, "revenu_mensuel": 5400})

    assert result["prediction"] == 0
    assert result["label"] == "risque_attrition_faible"


def test_predict_at_or_above_threshold_returns_high_attrition_risk(monkeypatch):
    service = build_service(monkeypatch, threshold=0.30)
    monkeypatch.setattr(service, "predict_proba", lambda _input: 0.30)

    result = service.predict({"age": 38, "revenu_mensuel": 5400})

    assert result["prediction"] == 1
    assert result["label"] == "risque_attrition_important"
