from pathlib import Path


class Settings:
    APP_NAME = "Estatora"
    APP_VERSION = "1.0.0"
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    MODEL_PATH = PROJECT_ROOT / "models" / "best_house_price_model.joblib"
    METRICS_PATH = PROJECT_ROOT / "models" / "metadata.json"


settings = Settings()
