import logging
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from app.config import settings
from app.schemas import HousePriceRequest
from app.services.model_service import model_service


logger = logging.getLogger(__name__)


app = FastAPI(
    title="Estatora API",
    version=settings.APP_VERSION,
    description="Prediction service for Estatora house valuations.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "HEAD", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/")
def root() -> Dict[str, Any]:
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "ok",
    }


@app.api_route("/api/health", methods=["GET", "HEAD"])
def health() -> Dict[str, Any]:
    ready = model_service.ready
    status = "healthy" if ready else "degraded"
    return {
        "status": status,
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "model_loaded": model_service.loaded,
        "prediction_ready": ready,
    }


@app.get("/api/model-info")
def model_info() -> Dict[str, Any]:
    return model_service.model_info()


@app.get("/api/metrics")
def metrics() -> Dict[str, Any]:
    payload = model_service.metrics
    if not payload:
        return {"model": model_service.model_name, "metrics": []}
    if "metrics" in payload:
        return {"model": model_service.model_name, "metrics": payload["metrics"]}
    return {"model": model_service.model_name, "metrics": payload}


@app.get("/api/docs")
def api_docs_redirect() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.post("/api/predict")
def predict(payload: HousePriceRequest) -> Dict[str, Any]:
    if not model_service.ready:
        raise HTTPException(status_code=503, detail="Model is not loaded and prediction is unavailable.")

    try:
        prediction = model_service.predict(payload.model_dump(by_alias=True, exclude_none=True))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive guard
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail="Prediction failed.") from exc

    return {
        "status": "success",
        "predicted_price": round(float(prediction), 2),
        "currency": "USD",
        "message": "Estimated sale price based on the trained Ames housing model.",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
