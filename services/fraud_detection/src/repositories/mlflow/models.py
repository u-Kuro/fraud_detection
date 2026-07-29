from typing import Any

import mlflow

from services.fraud_detection.src.modules.schemas.mlflow import DeployedModel

class MlflowModel:
    def __init__(self, deployed_model: DeployedModel):
        self.deployed_model = deployed_model
        self.model: Any = mlflow.sklearn.load_model(
            model_uri=f"models:/{deployed_model.model_name}/{deployed_model.model_version}"
        )