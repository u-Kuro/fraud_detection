import mlflow
from mlflow import MlflowClient

from dags.shared.modules.configs.mlflow import MLFlowConfig

mlflow.set_tracking_uri(mlflow_environment.MLFLOW_TRACKING_URI)

mlflow_client: MlflowClient = MlflowClient(
    tracking_uri=MLFlowConfig.MLFLOW_TRACKING_URI
)
mlflow_client.set_wo