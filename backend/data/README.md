# Local training data

The Ames Housing CSV is not included in this repository because the available Kaggle mirror lists its license as `Unknown`. Obtain a copy from a source whose terms permit your intended use and save it locally as `house-price.csv`.

The training scripts expect the Ames dataset fields `Order`, `PID`, and `SalePrice` in addition to the predictor columns described in `../app/feature_schema.json`. The local CSV is ignored by Git.
