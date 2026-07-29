import mlflow
from mlflow import MlflowClient

from services.shared.modules.configs.mlflow import MLFlowConfig

mlflow.set_tracking_uri(MLFlowConfig.TRACKING_URI)
client: MlflowClient = MlflowClient()