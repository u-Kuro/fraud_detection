from airflow.sdk import task, get_current_context

from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.airflow.xcom import ReplaceExpiredModelXCom, DeleteExpiredModelXCom
from dags.shared.modules.configs.mlflow import MLFlowConfig
from dags.shared.repositories.mlflow import mlflow_client

@task(task_id="replace_expired_model")
def replace_expired_model() -> None:
    context = get_current_context()

    replace_expired_model_xcom = ReplaceExpiredModelXCom.from_context(context)

    mlflow_client.set_registered_model_alias(
        name=replace_expired_model_xcom.replacement_model_name,
        alias=MLFlowConfig.CHALLENGER_ALIAS,
        version=str(replace_expired_model_xcom.replacement_model_version),
    )

@task(task_id="delete_expired_model")
def delete_expired_model() -> None:
    context = get_current_context()

    delete_expired_model_xcom = DeleteExpiredModelXCom.from_context(context)

    mlflow_client.delete_model_version(
        name=delete_expired_model_xcom.expired_model_name,
        version=str(delete_expired_model_xcom.expired_model_version),
    )