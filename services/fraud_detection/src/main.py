from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from multiprocessing import cpu_count

from fastapi import FastAPI
from services.fraud_detection.src.services.slack import start_socket_mode
from services.fraud_detection.src.modules.configs.fraud_classifier import FraudClassifierConfig
from services.fraud_detection.src.services.fraud_classifier import FraudClassifier
from services.fraud_detection.src.controllers.routers import predict

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = FraudClassifier(
        mlflow_model_uri=FraudClassifierConfig.deployed_model(),
    )
    app.state.executor = ThreadPoolExecutor(max_workers=cpu_count())

    start_socket_mode()

    yield

    app.state.executor.shutdown(wait=False)

app = FastAPI(
    title="Fraud Detection API",
    version="1.0.0",
    lifespan=lifespan,
)

# Routers
app.include_router(predict.router)

# Root
@app.get("/", include_in_schema=False)
async def root(): return "Fraud Detection API — visit /docs"