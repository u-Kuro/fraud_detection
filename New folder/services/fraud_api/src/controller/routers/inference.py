from fastapi import APIRouter, HTTPException

from services.fraud_api.src.main import fraud_classifier, inference_repository
from services.fraud_api.src.modules.schemas import TransactionDetails, ClassificationResponse
from services.shared.logging import logger

router = APIRouter(prefix="inference", tags=["inference"])

@router.post("/classify")
def classify(transaction_details: TransactionDetails) -> ClassificationResponse:
    if fraud_classifier is None:
        raise HTTPException(status_code=503, detail="Model failed to load.")

    if inference_repository is None:
        raise HTTPException(status_code=503, detail="Inference repository failed to load.")

    try:
        transaction_inference = fraud_classifier.classify(transaction_details)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Bad input: {exc}")
    except Exception as exc:
        logger.error(f"Prediction error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Inference error.")

    if inference_repository is not None:
        inference_repository.insert(transaction_inference)

    return ClassificationResponse(
        **transaction_inference.model_dump(include=ClassificationResponse.model_fields.keys())
    )