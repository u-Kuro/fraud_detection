import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from services.fraud_detection.src.modules.schemas.inferences.fraud_classification import FraudClassificationResponse, FraudClassificationRequest
from services.fraud_detection.src.repositories.postgres.transaction_inferences import insert_transaction_inference
from services.fraud_detection.src.services.dependencies import get_executor, get_model
from services.fraud_detection.src.services.fraud_classifier import FraudClassifier

router = APIRouter(prefix="/predict", tags=["predict"])

@router.post("/")
async def predict(
    transaction_details: FraudClassificationRequest,
    background_tasks: BackgroundTasks,
    model: FraudClassifier = Depends(get_model),
    executor: ThreadPoolExecutor = Depends(get_executor),
) -> FraudClassificationResponse:

    try:
        transaction_inference = await asyncio.get_running_loop().run_in_executor(
            executor,
            model.classify,
            transaction_details
        )

        background_tasks.add_task(
            insert_transaction_inference,
            transaction_inference=transaction_inference
        )

        return FraudClassificationResponse(
            **transaction_inference.model_dump(
                include=FraudClassificationResponse.model_fields.keys()
            )
        )
    except Exception as exception:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exception}")