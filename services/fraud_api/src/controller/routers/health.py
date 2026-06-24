from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from services.fraud_api.src.main import fraud_classifier
from services.fraud_api.src.modules.schemas import HealthResponse
from services.fraud_api.src.repositories.postgres import engine

router = APIRouter(prefix="/health", tags=["ops"])

@router.get("/live")
def health_live() -> HealthResponse:
    model_loaded = fraud_classifier is not None
    return HealthResponse(status="live", model_loaded=model_loaded)

@router.get("/ready")
def health_ready() -> HealthResponse:
    if fraud_classifier is None:
        raise HTTPException(status_code=503, detail="Model not loaded.")

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"DB not ready: {exc}")

    return HealthResponse(status="ready", model_loaded=True)

@router.get("/", include_in_schema=False)
def health_check():
    return health_ready()