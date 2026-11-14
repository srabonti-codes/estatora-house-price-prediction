import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


absence = [
    "Alley",
    "Bsmt Qual",
    "Bsmt Cond",
    "Bsmt Exposure",
    "BsmtFin Type 1",
    "BsmtFin Type 2",
    "Fireplace Qu",
    "Garage Type",
    "Garage Finish",
    "Garage Qual",
    "Garage Cond",
    "Pool QC",
    "Fence",
    "Misc Feature",
]


def get_feature_defaults(features: pd.DataFrame) -> dict[str, object]:
    defaults: dict[str, object] = {}
    for column in features.columns:
        values = features[column].dropna()
        if (
            pd.api.types.is_numeric_dtype(features[column])
            and column not in {"MS SubClass", "Mo Sold"}
        ):
            value = values.median() if not values.empty else None
        else:
            modes = values.mode()
            value = modes.iloc[0] if not modes.empty else None
        defaults[column] = value.item() if isinstance(value, np.generic) else value
    return defaults


class AmesFeatures(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        self.feature_names_in_ = np.array(X.columns, dtype=object)
        return self

    def transform(self, X):
        x = X.copy()
        for c in set(absence) & set(x):
            x[c] = x[c].fillna("None").replace("NA", "None")
        for c in ["MS SubClass", "Mo Sold"]:
            if c in x:
                x[c] = x[c].astype("Int64").astype("string")
        bad = (x["Garage Yr Blt"] < 1800) | (x["Garage Yr Blt"] > x["Yr Sold"])
        x.loc[bad, "Garage Yr Blt"] = np.nan
        x["TotalSF"] = (
            x[["Total Bsmt SF", "1st Flr SF", "2nd Flr SF"]].fillna(0).sum(axis=1)
        )
        x["TotalBathrooms"] = x[["Full Bath", "Bsmt Full Bath"]].fillna(0).sum(
            axis=1
        ) + 0.5 * x[["Half Bath", "Bsmt Half Bath"]].fillna(0).sum(axis=1)
        x["TotalPorchSF"] = (
            x[
                [
                    "Open Porch SF",
                    "Enclosed Porch",
                    "3Ssn Porch",
                    "Screen Porch",
                    "Wood Deck SF",
                ]
            ]
            .fillna(0)
            .sum(axis=1)
        )
        x["HouseAgeAtSale"] = (x["Yr Sold"] - x["Year Built"]).clip(lower=0)
        x["YearsSinceRemodel"] = (x["Yr Sold"] - x["Year Remod/Add"]).clip(lower=0)
        for src, dst in [
            ("Garage Area", "HasGarage"),
            ("Total Bsmt SF", "HasBasement"),
            ("Fireplaces", "HasFireplace"),
            ("Pool Area", "HasPool"),
        ]:
            x[dst] = (x[src].fillna(0) > 0).astype(int)
        return x
