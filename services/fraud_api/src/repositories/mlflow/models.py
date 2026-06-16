from typing import Any

import mlflow
from services.fraud_api.src.modules.schemas import MlflowModelUri, DeployedModel
from services.fraud_api.src.repositories.mlflow import client
from shared.logging import logger

class MlflowModel:
    def __init__(self, mlflow_model_uri: MlflowModelUri, class_name: str):
        self.model_uri = mlflow_model_uri.model_uri
        self.model: Any = mlflow.sklearn.load_model(
            model_uri=self.model_uri
        )
        self.deployed_model = self.get_deployed_model()
        logger.info(f"{class_name} loaded: {self.model_uri} → version {self.model_version}")

    def get_deployed_model(self) -> DeployedModel:
        try:
            model_path = self.model_uri.replace("models:/", "")

            # Handle Alias strings ("model@production")
            if "@" in model_path:
                model_name, model_alias = model_path.split("@")
                model_version = client.get_model_version_by_alias(
                    name=model_name, alias=model_alias
                )
                return DeployedModel(
                    model_name=model_name, model_version=int(model_version.version)
                )

            # Handle Version strings ("model/5")
            elif "/" in model_path:
                model_name, model_version = model_path.split("/")

                # If it's already a digit string (e.g., "5"), just use it directly
                if model_version.isdigit():
                    return DeployedModel(
                        model_name=model_name, model_version=int(model_version)
                    )

            raise ValueError(f"Invalid model URI format: {self.model_uri}")
        except Exception as exception:
            logger.warning(f"Could not resolve version: {exception}")
            raise exception
