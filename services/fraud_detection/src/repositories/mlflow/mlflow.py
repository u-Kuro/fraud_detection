import mlflow
from mlflow import MlflowClient
from services.shared.modules.configs import mlflow_config

mlflow.set_tracking_uri(mlflow_config.TRACKING_URI)
client: MlflowClient = MlflowClient()