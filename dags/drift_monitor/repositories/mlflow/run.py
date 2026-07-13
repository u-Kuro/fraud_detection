from airflow.sdk import task

from dags.drift_monitor.modules.schemas.airflow.xcom import DeleteExpiredMLFlowRunXCom
from dags.shared.repositories.mlflow import mlflow_client

@task(task_id="delete_expired_mlflow_run")
def delete_expired_mlflow_run(**context) -> None:
    delete_expired_mlflow_run_xcom = DeleteExpiredMLFlowRunXCom.from_context(context)

    mlflow_client.delete_run(run_id=delete_expired_mlflow_run_xcom.expired_mlflow_run_id)