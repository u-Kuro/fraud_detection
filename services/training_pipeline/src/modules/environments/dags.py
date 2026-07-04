from uuid import UUID

from pydantic_settings import BaseSettings, SettingsConfigDict

class DagsEnvironment(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, strict=False)

    MODEL_DEPLOYMENT_WORKFLOW_ID: UUID

dags_environment = DagsEnvironment()