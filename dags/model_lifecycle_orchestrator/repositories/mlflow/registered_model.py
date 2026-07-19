from airflow.sdk import task

from dags.model_lifecycle_orchestrator.modules.schemas.airflow.xcom import ReplaceExpiredModelXCom, \
    DeleteExpiredModelXCom
from dags.shared.modules.configs.airflow.data_keys import ModelDeploymentSuccessionKeys
from dags.shared.modules.configs.mlflow import MLFlowConfig
from dags.shared.modules.schemas.airflow import AirflowTaskContext
from dags.shared.repositories.mlflow import mlflow_client

@task(task_id="replace_expired_model")
def replace_expired_model(**context) -> None:
    replace_expired_model_xcom = ReplaceExpiredModelXCom.from_context(context)

    mlflow_client.set_registered_model_alias(
        name=replace_expired_model_xcom.replacement_model_name,
        alias=MLFlowConfig.CHALLENGER_ALIAS,
        version=str(replace_expired_model_xcom.replacement_model_version),
    )

    ti = AirflowTaskContext.from_context(context).ti
    ti.xcom_push(
        key=ModelDeploymentSuccessionKeys.EXPIRED_MODEL_NAME_KEY,
        value=replace_expired_model_xcom.expired_model_name
    )
    ti.xcom_push(
        key=ModelDeploymentSuccessionKeys.EXPIRED_MODEL_VERSION_KEY,
        value=replace_expired_model_xcom.expired_model_version
    )

    ti.xcom_push(
        key=ModelDeploymentSuccessionKeys.EXPIRED_MLFLOW_RUN_ID_KEY,
        value=replace_expired_model_xcom.expired_mlflow_run_id
    )

    ti.xcom_push(
        key=ModelDeploymentSuccessionKeys.EXPIRED_ID_KEY,
        value=replace_expired_model_xcom.expired_id
    )

@task(task_id="delete_expired_model")
def delete_expired_model(**context) -> None:
    delete_expired_model_xcom = DeleteExpiredModelXCom.from_context(context)

    mlflow_client.delete_model_version(
        name=delete_expired_model_xcom.expired_model_name,
        version=str(delete_expired_model_xcom.expired_model_version),
    )

    ti = AirflowTaskContext.from_context(context).ti
    ti.xcom_push(
        key=ModelDeploymentSuccessionKeys.EXPIRED_MLFLOW_RUN_ID_KEY,
        value=delete_expired_model_xcom.expired_mlflow_run_id
    )

    ti.xcom_push(
        key=ModelDeploymentSuccessionKeys.EXPIRED_ID_KEY,
        value=delete_expired_model_xcom.expired_id
    )