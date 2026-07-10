from pydantic_settings import BaseSettings, SettingsConfigDict

from dags.shared.modules.configs import airflow_config

class SlackEnvironment(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix=airflow_config.ENVIRONMENT_PREFIX,
        case_sensitive=True
    )

    SLACK_CHANNEL_ID: str

slack_environment = SlackEnvironment()