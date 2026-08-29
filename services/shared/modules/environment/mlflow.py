from pydantic_settings import BaseSettings, SettingsConfigDict

class MLflowEnvironment(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    # MLFLOW_TRACKING_URI: str
    # MLFLOW_TRACKING_USERNAME: str
    # MLFLOW_TRACKING_PASSWORD: str
    MLFLOW_WORKSPACE: str

mlflow_environment = MLflowEnvironment()