from airflow.sdk import task

from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.airflow.tasks import ExpiredAndReservedModelDeploymentWorkflows
from dags.shared.modules.configs.mlflow import MLFlowConfig
from dags.shared.repositories.mlflow.mlflow import mlflow_client

@task
def replace_expired_model(data: ExpiredAndReservedModelDeploymentWorkflows | None):
    assert data is not None

    mlflow_client.set_registered_model_alias(
        name=data.reserved.model_name,
        alias=MLFlowConfig.challenger_alias,
        version=str(data.reserved.model_version),
    )

@task
def delete_expired_model(data: ExpiredAndReservedModelDeploymentWorkflows | None):
    assert data is not None

    mlflow_client.delete_model_version(
        name=data.expired.model_name,
        version=str(data.expired.model_version),
    )