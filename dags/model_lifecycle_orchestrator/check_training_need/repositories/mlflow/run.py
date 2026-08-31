from airflow.sdk import task

from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.airflow.tasks import ExpiredAndReservedModelDeploymentWorkflows
from dags.shared.repositories.mlflow.mlflow import mlflow_client

@task
def delete_expired_mlflow_run(data: ExpiredAndReservedModelDeploymentWorkflows | None):
    assert data is not None

    mlflow_client.delete_run(run_id=data.expired.mlflow_run_id)