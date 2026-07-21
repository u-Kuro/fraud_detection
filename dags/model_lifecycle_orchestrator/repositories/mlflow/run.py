from airflow.sdk import task

from dags.model_lifecycle_orchestrator.modules.schemas.airflow.xcom import DeleteExpiredMLFlowRunXCom
from dags.shared.modules.configs.airflow.data_keys import ModelDeploymentSuccessionKeys
from dags.shared.modules.schemas.airflow import AirflowTaskContext
from dags.shared.repositories.mlflow import mlflow_client

@task(task_id="delete_expired_mlflow_run")
def delete_expired_mlflow_run(**context) -> None:
    delete_expired_mlflow_run_xcom = DeleteExpiredMLFlowRunXCom.from_context(context)

    mlflow_client.delete_run(run_id=delete_expired_mlflow_run_xcom.expired_mlflow_run_id)

    ti = AirflowTaskContext.from_context(context).ti
    ti.xcom_push(
        key=ModelDeploymentSuccessionKeys.EXPIRED_MODEL_NAME,
        value=delete_expired_mlflow_run_xcom.expired_id
    )