from pydantic_settings import BaseSettings, SettingsConfigDict

from dags.shared.modules.configs.airflow.airflow import AirflowConfig

class SlackEnvironment(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix=AirflowConfig.environment_prefix(),
        case_sensitive=True
    )

    SLACK_CHANNEL_ID: str

slack_environment = SlackEnvironment()