import json
from pathlib import Path
from typing import Optional

from pydantic import ConfigDict, Field, create_model


_FEATURE_SCHEMA_PATH = Path(__file__).with_name("feature_schema.json")
with _FEATURE_SCHEMA_PATH.open("r", encoding="utf-8") as schema_file:
    _FEATURE_SCHEMA = json.load(schema_file)

_NUMERIC_FEATURES = _FEATURE_SCHEMA["numeric"]
_INTEGER_FEATURES = set(_FEATURE_SCHEMA["integer"])
_CATEGORICAL_FEATURES = _FEATURE_SCHEMA["categorical"]
_FEATURE_FIELDS = {}
for feature in _NUMERIC_FEATURES:
    feature_type = Optional[int] if feature in _INTEGER_FEATURES else Optional[float]
    _FEATURE_FIELDS[feature] = (feature_type, Field(default=None))

_FEATURE_FIELDS.update(
    {
        feature: (Optional[str], Field(default=None))
        for feature in _CATEGORICAL_FEATURES
    }
)

HousePriceRequest = create_model(
    "HousePriceRequest",
    __config__=ConfigDict(
        extra="forbid",
        populate_by_name=True,
        allow_inf_nan=False,
    ),
    **_FEATURE_FIELDS,
)
