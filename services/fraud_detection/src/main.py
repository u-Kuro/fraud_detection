from contextlib import asynccontextmanager

from fastapi import FastAPI

from services.fraud_detection.src.controller.routers.slack import start_socket_mode
from services.fraud_detection.src.services import model_states
from services.fraud_detection.src.services.fraud_classifier import FraudClassifier
from services.fraud_detection.src.controller.routers import health, inference, slack
from shared.modules.configs import mlflow_config
from shared.modules.logging import logger

@asynccontextmanager
async def lifespan(_):
    try:
        model_states.fraud_classifier = FraudClassifier(
            mlflow_model_uri=mlflow_config.MODEL_URI,
        )
    except Exception as exception:
        logger.critical(f"Startup failed: {exception}", exc_info=True)
        raise RuntimeError("Startup failed") from exception

    start_socket_mode()

    yield

    logger.info("Shutting down.")

app = FastAPI(
    title="Fraud Detection API",
    version="1.0.0",
    lifespan=lifespan,
)

# Routers
app.include_router(health.router)
app.include_router(inference.router)
app.include_router(slack.router)

@app.get("/", include_in_schema=False)
def root():
    return {"message": "Fraud Detection API — visit /docs"}
