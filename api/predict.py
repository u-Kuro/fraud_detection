"""
api/predict.py — Model loading and inference

Kept separate from main.py so:
  - Concerns are split (loading vs serving vs monitoring)
  - Easy to swap model flavor later (pyfunc, onnx, pytorch, etc.)
  - Easy to unit test without starting FastAPI
"""

import logging, time
from typing import Any

import mlflow
import pandas as pd
from api.schemas import DeployedModel, MlflowModelFeatures, MlflowModelFlavor, MlflowModelUri, PredictionRequest, TransactionInference
from mlflow import MlflowClient

logger = logging.getLogger(__name__)

class ModelPredictor:
    """
    Wraps an MLflow model. Load once, call predict() many times.

    Args:
        model_uri: Any MLflow URI format:
            "models:/model@production"  ← alias (what you have)
            "models:/model/5"           ← specific version
    """
    def __init__(self, model_uri: MlflowModelUri, flavor: MlflowModelFlavor):
        self.model_uri = model_uri.model_uri
        mlflow_flavors = {
            "sklearn": mlflow.sklearn,
            "pyfunc": mlflow.pyfunc
        }
        self.flavor = flavor.flavor
        self.model: Any = mlflow_flavors[self.flavor].load_model(model_uri=self.model_uri)
        model_info = self._get_model_info()
        self.model_name = model_info.model_name
        self.model_version = model_info.model_version
        logger.info(f"Model loaded: {model_uri} → version {self.model_version}")

    def predict(
        self,
        request: PredictionRequest,
        start_time: float = time.perf_counter()
    ) -> TransactionInference:
        """
       Run inference on one transaction.

       Uses DataFrame (not list/array) so model validates feature names.
       This catches column ordering bugs that would otherwise be silent errors.
       """
        features = request.model_dump(include=MlflowModelFeatures.model_fields.keys())

        features_df = pd.DataFrame([features])
        features_df["transaction_timestamp"] = features_df["transaction_timestamp"].apply(lambda x: int(x.timestamp()))

        prediction = int(self.model.predict(features_df)[0])
        if self.flavor == "sklearn":
            fraud_probability = self.model.predict_proba(features_df)[0][1]
        else:
            fraud_probability = self.model.predict(data=features_df, params={"probabilities": True})[0][1]

        return TransactionInference(
            **request.model_dump(),
            is_fraud=None,
            is_fraud_probability=float(fraud_probability),
            is_fraud_prediction=prediction == 1,
            model_name=self.model_name,
            model_version=self.model_version,
            latency_ms=round((time.perf_counter() - start_time) * 1000, 2),
        )

    def _get_model_info(self) -> DeployedModel:
        try:
            client = MlflowClient()
            model_path = self.model_uri.replace("models:/", "")

            # Handle Alias strings ("model@production")
            if "@" in model_path:
                model_name, model_alias = model_path.split("@")
                model_version = client.get_model_version_by_alias(name=model_name, alias=model_alias)
                return DeployedModel(
                    model_name=model_name,
                    model_version=int(model_version.version)
                )

            # Handle Version strings ("model/5")
            elif "/" in model_path:
                model_name, model_version = model_path.split("/")

                # If it's already a digit string (e.g., "5"), just use it directly
                if model_version.isdigit():
                    return DeployedModel(
                        model_name=model_name,
                        model_version=int(model_version)
                    )

            raise ValueError(f"Invalid model URI format: {self.model_uri}")
        except Exception as exception:
            logger.warning(f"Could not resolve version: {exception}")
            raise exception