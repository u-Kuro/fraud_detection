from fastapi import APIRouter, HTTPException
from sqlalchemy import text, select

from services.fraud_detection.src.modules.schemas.health import HealthResponse
from services.fraud_detection.src.repositories.postgres.postgres import sql_session
from services.fraud_detection.src.services import model_states

router = APIRouter(prefix="/health", tags=["ops"])

@router.get("/", include_in_schema=False)
def health_check():
    if model_states.fraud_classifier is None:
        raise HTTPException(status_code=503, detail="Model is still not loaded.")

    try:
        with sql_session.begin() as session: session.execute(select(1))
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"DB is still not ready: {exc}")

    return HealthResponse(status="ok")