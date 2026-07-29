from dataclasses import dataclass
from functools import lru_cache

from services.fraud_detection.src.modules.schemas.mlflow import DeployedModel
from services.fraud_detection.src.repositories.postgres.model_deployments import get_active_model_deployment

@dataclass(frozen=True)
class FraudClassifierConfig:

    CLASSIFICATION_THRESHOLD: float = 0.5

    @classmethod
    @lru_cache(maxsize=None)
    def DEPLOYED_MODEL(self) -> DeployedModel:
        return get_active_model_deployment()