from pydantic import StrictStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from dags.shared.modules.configs.airflow.airflow import AirflowConfig

class S3Environment(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix=AirflowConfig.environment_prefix,
        case_sensitive=True
    )

    S3_CONNECTION_ID: StrictStr
    S3_BUCKET: StrictStr

s3_environment = S3Environment()