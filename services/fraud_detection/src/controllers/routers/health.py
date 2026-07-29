from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from services.fraud_detection.src.modules.schemas.health import HealthResponse
from services.fraud_detection.src.repositories.postgres.postgres import engine
from services.fraud_detection.src.services import model_states

router = APIRouter(prefix="/health", tags=["ops"])

@router.get("/", include_in_schema=False)
def health_check():
    if model_states.fraud_classifier is None:
        raise HTTPException(status_code=503, detail="Model is still not loaded.")

    try:
        with engine.connect() as connection: connection.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"DB is still not ready: {exc}")

    return HealthResponse(status="ok")