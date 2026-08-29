from os import environ
from typing import Type

import mlflow
from mlflow import MlflowClient

from dags.shared.modules.environment.mlflow import mlflow_environment

def initialize_mlflow():
    # Sets prefixed Apache Airflow environment to its official environment name
    environ["MLFLOW_TRACKING_USERNAME"] = mlflow_environment.MLFLOW_TRACKING_USERNAME
    environ["MLFLOW_TRACKING_PASSWORD"] = mlflow_environment.MLFLOW_TRACKING_PASSWORD

    mlflow.set_tracking_uri(mlflow_environment.MLFLOW_TRACKING_URI)
    mlflow.set_workspace(mlflow_environment.MLFLOW_WORKSPACE)

def get_mlflow_client() -> MlflowClient:
    initialize_mlflow()
    return MlflowClient(
        tracking_uri=mlflow_environment.MLFLOW_TRACKING_URI
    )

def get_mlflow():
    initialize_mlflow()
    return mlflow

mlflow_client: MlflowClient = get_mlflow_client()
mlflow_module = get_mlflow()