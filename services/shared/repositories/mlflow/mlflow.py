import mlflow
from mlflow import MlflowClient

from dags.shared.modules.environment.mlflow import mlflow_environment
from services.shared.modules.configs.mlflow import MLFlowConfig

def initialize_mlflow():
    # mlflow.set_tracking_uri(mlflow_environment.MLFLOW_TRACKING_URI)
    mlflow.set_workspace(mlflow_environment.MLFLOW_WORKSPACE)
    mlflow.set_experiment(MLFlowConfig.experiment_name)

def get_mlflow_client() -> MlflowClient:
    initialize_mlflow()
    return MlflowClient()

def get_mlflow():
    initialize_mlflow()
    return mlflow

mlflow_client: MlflowClient = get_mlflow_client()
mlflow_module = get_mlflow()