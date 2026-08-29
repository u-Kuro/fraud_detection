from pydantic_settings import BaseSettings, SettingsConfigDict

from dags.shared.modules.configs.airflow.airflow import AirflowConfig

class GitHubEnvironment(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix=AirflowConfig.environment_prefix,
        case_sensitive=True
    )

    GITHUB_CONNECTION_ID: str
    GITHUB_TOKEN: str = "test" # Not needed for nektos/act

github_environment = GitHubEnvironment()