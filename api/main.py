"""
api/main.py — Fraud Detection Prediction API

Loads the MLflow model once at startup,
then serves /health and /predict.

Run locally without Docker:
    uvicorn api.main:app --reload --port 8000
"""
import logging, time
from contextlib import asynccontextmanager

import mlflow
from fastapi import FastAPI, HTTPException
from api.monitoring import InferenceLogger
from api.predict import ModelPredictor
from api.schemas import Environment, PredictionRequest, PredictionResponse, TransactionInference

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

environment: Environment = Environment()
predictor: ModelPredictor | None = None
monitor: InferenceLogger | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once when the server starts, then yields to serve requests,
    then runs cleanup when the server stops.
    """
    global predictor, monitor

    tracking_uri = environment.MLFLOW_TRACKING_URI
    model_uri = environment.mlflow_model_uri
    model_flavor = environment.mlflow_model_flavor

    mlflow.set_tracking_uri(tracking_uri)
    logger.info(f"MLflow tracking URI: {tracking_uri}")

    logger.info(f"Loading model: {model_uri.model_uri}")
    predictor = ModelPredictor(model_uri=model_uri, flavor=model_flavor)

    # InferenceLogger connects to Postgres and creates the inference_logs table
    # if it doesn't exist. Monitoring failures never kill predictions.
    try:
        monitor = InferenceLogger()
    except Exception as exception:
        logger.warning(f"InferenceLogger failed to initialize (non-fatal): {exception}")
        monitor = None

    logger.info(f"Model ready | version={predictor.model_version}")

    yield

    logger.info("Shutting down.")

app = FastAPI(
    title="Fraud Detection API",
    description=f"Serves {environment.MLFLOW_MODEL_URI} from MLflow Model Registry.",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health", tags=["ops"])
def health_check():
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model failed to load.")
    return {
        "status": "ok",
        "model_uri": predictor.model_uri,
        "model_version": predictor.model_version,
    }

@app.post("/predict", tags=["inference"])
def predict(request: PredictionRequest):
    """
    Predict whether a transaction is fraudulent.
    Send features as a flat dict of name → float.
    """
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model failed to load.")

    start_time = time.perf_counter()

    try:
        transaction_inference = predictor.predict(request=request, start_time=start_time)
    except ValueError as valueError:
        raise HTTPException(status_code=422, detail=f"Bad input: {valueError}")
    except Exception as exception:
        logger.error(f"Prediction error: {exception}", exc_info=True)
        raise HTTPException(status_code=500, detail="Inference error.")

    monitor.log_inference(transaction_inference)

    return PredictionResponse(
        **transaction_inference.model_dump(
            include=PredictionResponse.model_fields.keys()
        )
    )

@app.get("/", include_in_schema=False)
def root():
    return {"message": "Fraud Detection API — visit /docs"}