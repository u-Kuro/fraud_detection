from fastapi import APIRouter, HTTPException

from services.fraud_detection.src.main import fraud_classifier
from services.fraud_detection.src.modules.schemas import FraudClassificationRequest
from services.fraud_detection.src.repositories.postgres.transaction_inferences import insert_transaction_inference
from shared.logging import logger
from shared.schemas import FraudClassificationResponse

router = APIRouter(prefix="/inference", tags=["inference"])

@router.post("/classify")
def classify(transaction_details: FraudClassificationRequest) -> FraudClassificationResponse:
    if fraud_classifier is None:
        raise HTTPException(status_code=503, detail="Model failed to load.")

    try:
        transaction_inference = fraud_classifier.classify(transaction_details)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Bad input: {exc}")
    except Exception as exc:
        logger.error(f"Prediction error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Inference error.")

    insert_transaction_inference(transaction_inference)

    return FraudClassificationResponse(
        **transaction_inference.model_dump(include=FraudClassificationResponse.model_fields.keys())
    )