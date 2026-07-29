from contextlib import asynccontextmanager

from fastapi import FastAPI

from services.fraud_detection.src.controllers.routers.slack import start_socket_mode
from services.fraud_detection.src.modules.configs.fraud_classifier import FraudClassifierConfig
from services.fraud_detection.src.services import model_states
from services.fraud_detection.src.services.fraud_classifier import FraudClassifier
from services.fraud_detection.src.controllers.routers import health, inference, slack

@asynccontextmanager
async def lifespan(_):
    model_states.fraud_classifier = FraudClassifier(
        mlflow_model_uri=FraudClassifierConfig.DEPLOYED_MODEL(),
    )
    start_socket_mode()

    yield

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
