import mlflow
from mlflow import MlflowClient
from shared.configs import mlflow_config

mlflow.set_tracking_uri(mlflow_config.MLFLOW_TRACKING_URI)
client: MlflowClient = MlflowClient()