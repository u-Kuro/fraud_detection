from dataclasses import dataclass
from functools import lru_cache

from services.drift_check.src.repositories.postgres.model_deployments import get_active_model_deployment_mlflow_run_id
from services.shared.modules.configs import MLFlowConfig as BaseMLFlowConfig

@dataclass(frozen=True)
class MLFlowConfig(BaseMLFlowConfig):
    @classmethod
    @lru_cache(maxsize=None)
    def REFERENCE_DATASET_URI(self) -> str:
        return f"runs:/{get_active_model_deployment_mlflow_run_id()}/{MLFlowConfig.REFERENCE_DATASET_PATH}/{MLFlowConfig.REFERENCE_DATASET_FILE_NAME}/{self.REFERENCE_DATASET_FILE_NAME}"