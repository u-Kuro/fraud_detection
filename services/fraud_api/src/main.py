from contextlib import asynccontextmanager

from fastapi import FastAPI

from services.fraud_api.src.services.inference import FraudClassifier
from services.fraud_api.src.repositories.postgres.fraud_inference_repository import (
    FraudInferenceRepository,
)
from services.fraud_api.src.modules.environment import environment

from services.fraud_api.src.controller.routers import health, inference
from shared.logging import logger

fraud_classifier: FraudClassifier
inference_repository: FraudInferenceRepository

@asynccontextmanager
async def lifespan(_):
    try:
        global fraud_classifier, inference_repository

        fraud_classifier = FraudClassifier(
            mlflow_model_uri=environment.mlflow_model_uri,
        )
        inference_repository = FraudInferenceRepository()

    except Exception as exception:
        logger.critical(f"Startup failed: {exception}", exc_info=True)
        raise RuntimeError("Startup failed") from exception

    yield

    logger.info("Shutting down.")


app = FastAPI(
    title="Fraud Detection API",
    description="Serves models from MLflow Model Registry.",
    version="1.0.0",
    lifespan=lifespan,
)

# Routers
app.include_router(health.router)
app.include_router(inference.router)


@app.get("/", include_in_schema=False)
def root():
    return {"message": "Fraud Detection API — visit /docs"}
