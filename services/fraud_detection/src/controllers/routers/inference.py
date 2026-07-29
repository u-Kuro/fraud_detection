from fastapi import APIRouter, HTTPException

from services.fraud_detection.src.modules.schemas.inferences.fraud_classification import FraudClassificationResponse, FraudClassificationRequest
from services.fraud_detection.src.repositories.postgres.transaction_inferences import insert_transaction_inference
from services.fraud_detection.src.services import model_states

router = APIRouter(prefix="/inference", tags=["inference"])

@router.post("/classify")
def classify(transaction_details: FraudClassificationRequest) -> FraudClassificationResponse:
    fraud_classifier = model_states.fraud_classifier

    if fraud_classifier is None:
        raise HTTPException(status_code=503, detail="Model failed to load.")

    try:
        transaction_inference = fraud_classifier.classify(transaction_details)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Bad input: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Inference error: {exc}")

    insert_transaction_inference(transaction_inference)

    return FraudClassificationResponse(
        **transaction_inference.model_dump(include=FraudClassificationResponse.model_fields.keys())
    )