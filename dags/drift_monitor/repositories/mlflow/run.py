from airflow.sdk import task

from dags.drift_monitor.modules.schemas.mlflow import DeleteExpiredMLflowRunConfigurations
from dags.shared.repositories.mlflow import mlflow_client

@task(task_id="delete_expired_mlflow_run")
def delete_expired_mlflow_run(**context) -> None:
    configurations = DeleteExpiredMLflowRunConfigurations.from_context(context)

    mlflow_client.delete_run(run_id=configurations.expired_run_id)