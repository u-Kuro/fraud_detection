from dataclasses import dataclass
from functools import lru_cache

from services.drift_check.src.repositories.postgres.model_deployments import get_active_model_deployment_mlflow_run_id
from services.shared.modules.configs.mlflow import MLFlowConfig as BaseMLFlowConfig

@dataclass(frozen=True)
class MLFlowConfig(BaseMLFlowConfig):
    @classmethod
    @lru_cache(maxsize=None)
    def reference_dataset_uri(cls) -> str:
        return f"runs:/{get_active_model_deployment_mlflow_run_id()}/{MLFlowConfig.reference_dataset_path}/{MLFlowConfig.reference_dataset_file_name}"