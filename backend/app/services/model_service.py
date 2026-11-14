import json
import logging
from typing import Any, Dict, List

import joblib
import numpy as np
import pandas as pd

from app.config import settings


logger = logging.getLogger(__name__)


class ModelService:
    def __init__(self) -> None:
        self.model_bundle: Dict[str, Any] | None = None
        self.raw_columns: List[str] = []
        self.model_name = "XGBoost"
        self.metrics: Dict[str, Any] = {}
        self.loaded = False
        self.load_model()

    def load_model(self) -> bool:
        if not settings.MODEL_PATH.exists():
            self.loaded = False
            self.model_bundle = None
            return False

        try:
            bundle = joblib.load(settings.MODEL_PATH)
            self.model_bundle = bundle if isinstance(bundle, dict) else {"model": bundle}
            self.model_name = str(self.model_bundle.get("model_name", "XGBoost"))
            self.raw_columns = list(self.model_bundle.get("raw_columns", []))
            self.loaded = True
            self.metrics = self._load_metrics()
            return True
        except Exception:
            logger.exception("Could not load the prediction model from %s", settings.MODEL_PATH)
            self.loaded = False
            self.model_bundle = None
            return False

    def _load_metrics(self) -> Dict[str, Any]:
        if not settings.METRICS_PATH.exists():
            return {}
        try:
            with settings.METRICS_PATH.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            return payload
        except Exception:
            logger.exception("Could not load model metadata from %s", settings.METRICS_PATH)
            return {}

    @property
    def ready(self) -> bool:
        bundle = self.model_bundle
        if not self.loaded or bundle is None:
            return False

        defaults = bundle.get("feature_defaults")
        return (
            bundle.get("model") is not None
            and bundle.get("preprocessor") is not None
            and bool(self.raw_columns)
            and isinstance(defaults, dict)
            and all(column in defaults for column in self.raw_columns)
        )

    def predict(self, payload: Dict[str, Any]) -> float:
        if not self.ready:
            raise ValueError("Prediction model is unavailable.")

        bundle = self.model_bundle or {}
        preprocessor = bundle.get("preprocessor")
        model = bundle.get("model")
        if preprocessor is None or model is None:
            raise ValueError("Prediction pipeline is unavailable.")

        frame = self._build_dataframe(payload)
        transformed = preprocessor.transform(frame)
        prediction_log = model.predict(transformed)[0]
        return float(np.expm1(prediction_log))

    def _build_dataframe(self, payload: Dict[str, Any]) -> pd.DataFrame:
        bundle = self.model_bundle or {}
        defaults = bundle.get("feature_defaults")
        if not isinstance(defaults, dict):
            raise ValueError("Prediction defaults are unavailable; retrain the model.")

        missing_defaults = set(self.raw_columns) - defaults.keys()
        if missing_defaults:
            raise ValueError("The model bundle is missing feature defaults.")

        normalized = {column: defaults[column] for column in self.raw_columns}

        for key, value in payload.items():
            if key in self.raw_columns and value is not None:
                normalized[key] = value

        return pd.DataFrame([normalized], columns=self.raw_columns)

    def model_info(self) -> Dict[str, Any]:
        return {
            "application": "Estatora",
            "model_name": self.model_name,
            "target": "SalePrice",
            "currency": "USD",
            "unit": "dollars",
            "feature_count": len(self.raw_columns),
            "model_loaded": self.loaded,
            "prediction_ready": self.ready,
            "metrics": self.metrics.get("metrics", self.metrics),
        }


model_service = ModelService()
