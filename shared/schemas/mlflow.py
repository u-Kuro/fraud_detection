from pydantic_settings import BaseSettings, SettingsConfigDict

class MlflowModelConfig(BaseSettings):
    """
    MLflow model-registry configuration with overridable defaults.

    All values can be changed per-environment via env vars — no hardcoded
    model names or alias strings anywhere in calling code.
    """
    model_config = SettingsConfigDict(case_sensitive=True)

    MLFLOW_TRACKING_URI:          str = "http://mlflow:5000"
    MLFLOW_REGISTERED_MODEL_NAME: str = "XGBoost"
    MLFLOW_PRODUCTION_ALIAS:      str = "production"
    MLFLOW_CANDIDATE_ALIAS:       str = "candidate"
    MLFLOW_ARCHIVED_ALIAS:        str = "archived"
    MLFLOW_EXPERIMENT_NAME:       str = "fraud-detection"

    @property
    def MODEL_URI(self) -> str:
        return f"models:/{self.MLFLOW_REGISTERED_MODEL_NAME}@{self.MLFLOW_PRODUCTION_ALIAS}"