from pydantic_settings import BaseSettings, SettingsConfigDict

class DriftCheckEnvironment(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    ACTIVE_MODEL_DEPLOYMENT_MLFLOW_RUN_ID: str

drift_check_environment = DriftCheckEnvironment()