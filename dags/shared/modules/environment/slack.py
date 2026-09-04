from pydantic import StrictStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from dags.shared.modules.configs.airflow.airflow import AirflowConfig

class SlackEnvironment(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix=AirflowConfig.environment_prefix,
        case_sensitive=True
    )

    SLACK_CONNECTION_ID: StrictStr
    SLACK_CHANNEL_ID: StrictStr

slack_environment = SlackEnvironment()