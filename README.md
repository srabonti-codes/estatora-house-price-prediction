# Estatora

Estatora is a house-price estimation project built around the Ames, Iowa housing dataset. It combines a React form, a FastAPI prediction API, and a trainable XGBoost pipeline to estimate a property's sale price from selected property details.

This repository is a source-code and machine-learning showcase. The estimate is an educational prediction, not a real-estate appraisal or financial advice.

## Overview

The browser collects a focused set of property characteristics and sends them to the API. The backend fills unprovided model features with training-set medians or modes, applies the saved preprocessing pipeline, and returns a USD estimate.

The raw dataset and trained model are intentionally not included. Supply an appropriately licensed Ames Housing CSV and train a local model before requesting predictions.

## Features

- Responsive property-estimate form with common home, quality, size, and sale details.
- FastAPI endpoints for health, model information, local training metrics, and predictions.
- Ames-specific preprocessing and derived features, including total area, bathrooms, porch area, and age at sale.
- Median/mode defaults for model inputs not exposed in the form.
- Research notebook comparing linear regression, random forest, XGBoost, MLP, TabNet, and FT-Transformer.
- A committed feature schema allows the API to start without access to the raw dataset.
- Validation-based model selection in the notebook; the test split is reserved for final evaluation.

### Customer experience

Visitors provide common property characteristics such as neighborhood, quality, living area, lot size, year built, bathrooms, and garage size. The frontend submits these values and presents the predicted sale price in USD. Fields not shown in the form receive typical dataset values in the API.

### Consultation and administration

Estatora does not implement consultations, user accounts, administrator tools, or role-based permissions. The API and estimate form are public; there is no authentication or authorization layer.

## Technology

| Area | Technologies |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS 4, Lucide React |
| API | Python, FastAPI, Pydantic, Uvicorn |
| Data and modeling | pandas, NumPy, scikit-learn, XGBoost, joblib |
| Research notebook | Jupyter, Matplotlib, Seaborn, PyTorch |

## Architecture

```text
Browser
  └── React + Vite
        └── POST /api/predict
              └── FastAPI
                    ├── validates Ames feature fields
                    ├── supplies defaults for omitted values
                    └── loads the preprocessing/model bundle
                          └── XGBoost prediction in log-price space
```

The model service loads a locally generated `backend/models/best_house_price_model.joblib` bundle at API startup. The notebook and `backend/train_model.py` contain the feature-processing and training workflows.

## Repository structure

```text
.
├── backend/
│   ├── app/
│   │   ├── config.py
│   │   ├── feature_schema.json
│   │   ├── main.py
│   │   ├── schemas.py
│   │   └── services/model_service.py
│   ├── data/README.md
│   ├── models/
│   │   ├── ames_features.py
│   │   └── __init__.py
│   ├── notebooks/
│   │   ├── house-price-prediction.ipynb
│   │   └── requirements.txt
│   ├── requirements.txt
│   └── train_model.py
├── frontend/
│   ├── public/
│   ├── src/
│   ├── .env.example
│   ├── package.json
│   └── vite.config.js
├── .gitignore
├── LICENSE
└── README.md
```

## Prerequisites

- Python 3.11 or newer
- Node.js 20 or newer and npm

## Local setup

### Dataset and model setup

The repository does not include raw housing data or a pretrained model. Obtain an Ames Housing CSV from a source whose terms permit your use and save it as `backend/data/house-price.csv`. From `backend/`, install the dependencies and train the serving model:

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python train_model.py
```

Training writes `models/best_house_price_model.joblib` and `models/metadata.json` locally. These generated files and the dataset are ignored by Git.

### Backend API

After training, start the API from `backend/`:

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Without a locally generated model bundle, the API reports a degraded health status and prediction requests return `503`. No backend `.env` file or external service is required.

### Frontend

In a second terminal:

```powershell
cd frontend
npm ci
Copy-Item .env.example .env.local
npm run dev
```

Open the local URL printed by Vite. With `VITE_API_URL` left blank, development requests use the Vite `/api` proxy to reach `http://localhost:8000`. Set it to the API origin when the frontend and API are hosted separately. The value is compiled into the browser bundle and must never contain a secret.

## Environment configuration

`frontend/.env.example` documents the only application setting:

| Variable | Purpose | Example |
|---|---|---|
| `VITE_API_URL` | Optional API origin. Leave blank to use the development proxy or same-origin API. | `https://api.example.com` |

The backend has no environment-specific credentials or configuration variables. Do not put keys, passwords, or private values in `VITE_*` variables; frontend values are public.

## Development commands

Run these commands from `frontend/`:

| Command | Purpose |
|---|---|
| `npm run dev` | Start the Vite development server |
| `npm run build` | Create the frontend production bundle in `dist/` |
| `npm run preview` | Preview a previously created frontend build |

Run the API from `backend/` with `uvicorn app.main:app --reload`. The API documentation is available at `/docs` and `/api/docs`.

### Retraining and notebook

To retrain the serving XGBoost model using the fixed seed and split:

```powershell
cd backend
python train_model.py
```

This writes the API model bundle and local `metadata.json` using defaults learned from the training split. For the full multi-model research notebook, install its additional dependencies and launch it from `backend/`:

```powershell
python -m pip install -r notebooks/requirements.txt
jupyter lab notebooks/house-price-prediction.ipynb
```

The notebook selects a model using validation performance and then evaluates that selection against the held-out test split. Its notebook outputs are not committed; the source cells can be run to reproduce the analysis.

## API endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET`, `HEAD` | `/api/health` | Report API and model readiness |
| `POST` | `/api/predict` | Return an estimated sale price |
| `GET` | `/api/model-info` | Report model and target metadata |
| `GET` | `/api/metrics` | Return recorded model metrics |
| `GET` | `/api/docs` | Redirect to the FastAPI documentation |

The prediction request accepts optional fields from the committed Ames feature schema. Fields not provided by the caller are populated with training-set medians or modes stored in the local model bundle before preprocessing. The response includes `predicted_price` and `currency: "USD"`.

## Model and evaluation notes

The serving bundle contains an XGBoost regressor trained on `log1p(SalePrice)` and the corresponding preprocessing pipeline. The research notebook applies Ames-specific feature engineering, imputes missing values, scales numeric features, and one-hot encodes categorical features. Model selection is based on validation RMSE; the test split is reserved for final evaluation. Benchmark outputs are generated locally and are not committed.

The Ames dataset covers historical sales in Ames, Iowa. Estimates do not represent current market prices or a professional appraisal.

## Data attribution and licensing

The project is based on Dean De Cock, “Ames, Iowa: Alternative to the Boston Housing Data as an End of Semester Regression Project,” *Journal of Statistics Education*, 19(3), 2011. See the [article and dataset documentation](https://jse.amstat.org/v19n3/decock.pdf). A public Kaggle mirror of the dataset reports its license as `Unknown`, so this repository does not redistribute the CSV or a model trained from it. Obtain the data from a source whose terms permit your intended use.

The MIT license in this repository applies to original Estatora code only. Third-party dependencies and any locally obtained data or generated model retain their respective terms; neither the dataset nor a trained model is included here.

## Security and implementation notes

- The API has no authentication and is intended for public, non-sensitive estimates. Do not use it to process private customer data without adding appropriate access controls.
- CORS is open to browser origins for the public API, but credentialed cross-origin requests are disabled.
- `joblib` model files use Python object serialization. Load only model artifacts from a source you trust.
- The frontend API URL is public configuration, not a place for credentials.
- The API's omitted-feature defaults are computed from the training split and stored in the generated model bundle.
- The API can start without the dataset or model, but predictions require a locally trained bundle.
- No automated test suite is included in this repository at present.
