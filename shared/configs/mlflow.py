from pydantic import BaseModel, ConfigDict

class MLflowConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    MLFLOW_TRACKING_URI:          str = "http://mlflow:5000"
    MLFLOW_REGISTERED_MODEL_NAME: str = "XGBoost"
    MLFLOW_PRODUCTION_ALIAS:      str = "production"
    MLFLOW_CANDIDATE_ALIAS:       str = "candidate"
    MLFLOW_ARCHIVED_ALIAS:        str = "archived"
    MLFLOW_EXPERIMENT_NAME:       str = "fraud-detection"
    MODEL_URI: str = f"models:/{MLFLOW_REGISTERED_MODEL_NAME}@{MLFLOW_PRODUCTION_ALIAS}"

mlflow_config = MLflowConfig()