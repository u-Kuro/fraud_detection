import mlflow
from mlflow import MlflowClient

from dags.shared.modules.configs import mlflow_config

mlflow.set_tracking_uri(mlflow_config.TRACKING_URI)
mlflow.set_experiment(mlflow_config.EXPERIMENT_NAME)

mlflow_client: MlflowClient = MlflowClient(
    tracking_uri=mlflow_config.TRACKING_URI
)