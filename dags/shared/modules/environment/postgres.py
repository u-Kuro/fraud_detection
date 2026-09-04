from pydantic import StrictStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from dags.shared.modules.configs.airflow.airflow import AirflowConfig

class PostgresEnvironment(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix=AirflowConfig.environment_prefix,
        case_sensitive=True
    )

    POSTGRES_CONNECTION_ID: StrictStr

postgres_environment = PostgresEnvironment()