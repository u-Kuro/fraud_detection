from airflow.sdk.types import TaskInstance
from pydantic import BaseModel, ConfigDict

from dags.challenger_model_rotation.repositories.mlflow.registered_model import replace_expired_model, delete_expired_model
from dags.model_lifecycle_monitor.repositories.postgres.model_deployment_workflows import has_expired_promote_pending_workflow_with_replacement

from dags.shared.modules.configs.airflow.data_keys import ModelDeploymentSuccessionKeys
from dags.shared.modules.schemas.airflow import AirflowTaskContext

class ReplaceExpiredModelXCom(BaseModel):
    model_config = ConfigDict(strict=True)

    replacement_model_name: str
    replacement_model_version: int

    expired_model_name: str
    expired_model_version: int

    expired_mlflow_run_id: str

    @classmethod
    def from_context(cls, context: dict) -> "ReplaceExpiredModelXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            replacement_model_name=ti.xcom_pull(
                task_ids=has_expired_promote_pending_workflow_with_replacement.__name__,
                key=ModelDeploymentSuccessionKeys.REPLACEMENT_MODEL_NAME_KEY,
            ),
            replacement_model_version=ti.xcom_pull(
                task_ids=has_expired_promote_pending_workflow_with_replacement.__name__,
                key=ModelDeploymentSuccessionKeys.REPLACEMENT_MODEL_VERSION_KEY,
            ),
            expired_model_name=ti.xcom_pull(
                task_ids=has_expired_promote_pending_workflow_with_replacement.__name__,
                key=ModelDeploymentSuccessionKeys.EXPIRED_MODEL_NAME_KEY,
            ),
            expired_model_version=ti.xcom_pull(
                task_ids=has_expired_promote_pending_workflow_with_replacement.__name__,
                key=ModelDeploymentSuccessionKeys.EXPIRED_MODEL_VERSION_KEY,
            ),
            expired_mlflow_run_id = ti.xcom_pull(
                task_ids=has_expired_promote_pending_workflow_with_replacement.__name__,
                key=ModelDeploymentSuccessionKeys.EXPIRED_MLFLOW_RUN_ID_KEY,
            )
        )

class DeleteExpiredModelXCom(BaseModel):
    model_config = ConfigDict(strict=True)

    expired_model_name: str
    expired_model_version: int

    expired_mlflow_run_id: str

    @classmethod
    def from_context(cls, context: dict) -> "DeleteExpiredModelXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            expired_model_name=ti.xcom_pull(
                task_ids=replace_expired_model.__name__,
                key=ModelDeploymentSuccessionKeys.EXPIRED_MODEL_NAME_KEY,
            ),
            expired_model_version=ti.xcom_pull(
                task_ids=replace_expired_model.__name__,
                key=ModelDeploymentSuccessionKeys.EXPIRED_MODEL_VERSION_KEY,
            ),
            expired_mlflow_run_id=ti.xcom_pull(
                task_ids=replace_expired_model.__name__,
                key=ModelDeploymentSuccessionKeys.EXPIRED_MLFLOW_RUN_ID_KEY,
            )
        )

class DeleteExpiredMLFlowRunXCom(BaseModel):
    model_config = ConfigDict(strict=True)

    expired_mlflow_run_id: str

    @classmethod
    def from_context(cls, context: dict) -> "DeleteExpiredMLFlowRunXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            expired_mlflow_run_id=ti.xcom_pull(
                task_ids=delete_expired_model.__name__,
                key=ModelDeploymentSuccessionKeys.EXPIRED_MLFLOW_RUN_ID_KEY,
            )
        )