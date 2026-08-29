from os import environ

import mlflow
from mlflow import MlflowClient

from dags.shared.modules.environment.mlflow import mlflow_environment

# Sets prefixed Apache Airflow environment to its official environment name
environ["MLFLOW_TRACKING_USERNAME"] = mlflow_environment.MLFLOW_TRACKING_USERNAME
environ["MLFLOW_TRACKING_PASSWORD"] = mlflow_environment.MLFLOW_TRACKING_PASSWORD

mlflow.set_tracking_uri(mlflow_environment.MLFLOW_TRACKING_URI)
mlflow.set_workspace(mlflow_environment.MLFLOW_WORKSPACE)

mlflow_client: MlflowClient = MlflowClient(
    tracking_uri=mlflow_environment.MLFLOW_TRACKING_URI
)