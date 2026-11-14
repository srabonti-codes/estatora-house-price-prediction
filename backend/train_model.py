import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, RobustScaler
from xgboost import XGBRegressor

from models.ames_features import AmesFeatures, get_feature_defaults


ROOT = Path(__file__).resolve().parent
SEED = 42

data_path = ROOT / "data" / "house-price.csv"
if not data_path.exists():
    raise FileNotFoundError(
        "Place a licensed Ames Housing CSV at backend/data/house-price.csv before training."
    )

data = pd.read_csv(data_path, keep_default_na=False, na_values=[""])
data.columns = data.columns.str.strip()
for column in data.select_dtypes("object"):
    data[column] = data[column].str.strip()

data = data.drop_duplicates().reset_index(drop=True)
target = data.pop("SalePrice").astype(float)
features = data.drop(columns=["Order", "PID"])
train_validation, test_features, train_validation_target, test_target = train_test_split(
    features, target, test_size=0.15, random_state=SEED
)
train_features, _, train_target, _ = train_test_split(
    train_validation,
    train_validation_target,
    test_size=0.15 / 0.85,
    random_state=SEED,
)
feature_defaults = get_feature_defaults(train_features)

probe = AmesFeatures().fit_transform(train_features)
numeric_columns = probe.select_dtypes(include=np.number).columns
categorical_columns = probe.select_dtypes(exclude=np.number).columns
preprocessor = Pipeline(
    [
        ("features", AmesFeatures()),
        (
            "columns",
            ColumnTransformer(
                [
                    (
                        "num",
                        Pipeline(
                            [
                                ("impute", SimpleImputer(strategy="median", add_indicator=True)),
                                ("scale", RobustScaler()),
                            ]
                        ),
                        numeric_columns,
                    ),
                    (
                        "cat",
                        Pipeline(
                            [
                                ("impute", SimpleImputer(strategy="most_frequent")),
                                (
                                    "encode",
                                    OneHotEncoder(handle_unknown="ignore", sparse_output=False, min_frequency=2),
                                ),
                            ]
                        ),
                        categorical_columns,
                    ),
                ],
                verbose_feature_names_out=False,
            ),
        ),
    ]
)

transformed_train = preprocessor.fit_transform(train_features)
transformed_test = preprocessor.transform(test_features)
model = XGBRegressor(
    n_estimators=1200,
    learning_rate=0.03,
    max_depth=4,
    min_child_weight=2,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_lambda=1.0,
    objective="reg:squarederror",
    n_jobs=-1,
    random_state=SEED,
)
model.fit(transformed_train, np.log1p(train_target))
predictions = np.expm1(model.predict(transformed_test))
metric = {
    "Model": "XGBoost",
    "Split": "test",
    "MAE": float(mean_absolute_error(test_target, predictions)),
    "MSE": float(mean_squared_error(test_target, predictions)),
    "RMSE": float(mean_squared_error(test_target, predictions) ** 0.5),
    "R2": float(r2_score(test_target, predictions)),
}

models_directory = ROOT / "models"
models_directory.mkdir(exist_ok=True)
joblib.dump(
    {
        "model_name": "XGBoost",
        "model": model,
        "preprocessor": preprocessor,
        "selector": None,
        "deep": False,
        "raw_columns": features.columns.tolist(),
        "feature_defaults": feature_defaults,
        "log_target": True,
    },
    models_directory / "best_house_price_model.joblib",
)

metadata = {
    "best_model": "XGBoost",
    "seed": SEED,
    "rows": len(data),
    "splits": {
        "train": len(train_features),
        "validation": len(train_validation) - len(train_features),
        "test": len(test_features),
    },
    "metrics": [metric],
}
(models_directory / "metadata.json").write_text(
    json.dumps(metadata, indent=2),
    encoding="utf-8",
)
print(f"Saved XGBoost | RMSE ${metric['RMSE']:,.0f} | R² {metric['R2']:.3f}")
