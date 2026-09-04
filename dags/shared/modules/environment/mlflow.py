from pydantic import StrictStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from dags.shared.modules.configs.airflow.airflow import AirflowConfig

class MLflowEnvironment(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix=AirflowConfig.environment_prefix,
        case_sensitive=True
    )

    MLFLOW_TRACKING_URI: StrictStr
    MLFLOW_TRACKING_USERNAME: StrictStr
    MLFLOW_TRACKING_PASSWORD: StrictStr
    MLFLOW_WORKSPACE: StrictStr

mlflow_environment = MLflowEnvironment()