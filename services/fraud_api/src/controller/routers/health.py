from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import text

from services.fraud_api.src.main import fraud_classifier, inference_repository
from services.fraud_api.src.modules.schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["ops"])

@router.get("/live")
def health_live(request: Request) -> HealthResponse:
    model_loaded = fraud_classifier is not None
    return HealthResponse(status="live", model_loaded=model_loaded)

@router.get("/ready")
def health_ready() -> HealthResponse:
    if fraud_classifier is None:
        raise HTTPException(status_code=503, detail="Model not loaded.")

    if inference_repository is not None:
        try:
            with inference_repository.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"DB not ready: {exc}")

    return HealthResponse(status="ready", model_loaded=True)

@router.get("/", include_in_schema=False)
def health_check():
    return health_ready()