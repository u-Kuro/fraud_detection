import mlflow
from mlflow import MlflowClient

from dags.shared.modules.configs.mlflow import MLFlowConfig

mlflow.set_tracking_uri(MLFlowConfig.TRACKING_URI)
mlflow.set_experiment(MLFlowConfig.EXPERIMENT_NAME)

mlflow_client: MlflowClient = MlflowClient(
    tracking_uri=MLFlowConfig.TRACKING_URI
)