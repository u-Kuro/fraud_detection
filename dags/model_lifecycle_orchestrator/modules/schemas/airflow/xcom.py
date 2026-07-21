from enum import StrEnum, Enum
from uuid import UUID

from airflow.sdk.types import TaskInstance
from pydantic import BaseModel, ConfigDict

from dags.model_lifecycle_orchestrator.repositories.mlflow.registered_model import replace_expired_model, delete_expired_model
from dags.model_lifecycle_orchestrator.repositories.postgres.model_deployment_workflows import has_expired_promote_pending_workflow_with_replacement
from dags.model_lifecycle_orchestrator.services.tasks import drift_check_task_id, has_drift
from dags.shared.modules.configs.airflow.data_keys import ModelDeploymentSuccessionKeys, DriftMonitorKeys

from dags.shared.modules.schemas.airflow import AirflowTaskContext


class ReplaceExpiredModelXCom(BaseModel):
    model_config = ConfigDict(strict=True)

    replacement_model_name: str
    replacement_model_version: int

    @classmethod
    def from_context(cls, context: dict) -> "ReplaceExpiredModelXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            replacement_model_name=ti.xcom_pull(
                task_ids=has_expired_promote_pending_workflow_with_replacement.__name__,
                key=ModelDeploymentSuccessionKeys.REPLACEMENT_MODEL_NAME,
            ),
            replacement_model_version=ti.xcom_pull(
                task_ids=has_expired_promote_pending_workflow_with_replacement.__name__,
                key=ModelDeploymentSuccessionKeys.REPLACEMENT_MODEL_VERSION,
            )
        )

class DeleteExpiredModelXCom(BaseModel):
    model_config = ConfigDict(strict=True)

    expired_model_name: str
    expired_model_version: int

    @classmethod
    def from_context(cls, context: dict) -> "DeleteExpiredModelXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            expired_model_name=ti.xcom_pull(
                task_ids=has_expired_promote_pending_workflow_with_replacement.__name__,
                key=ModelDeploymentSuccessionKeys.EXPIRED_MODEL_NAME,
            ),
            expired_model_version=ti.xcom_pull(
                task_ids=has_expired_promote_pending_workflow_with_replacement.__name__,
                key=ModelDeploymentSuccessionKeys.EXPIRED_MODEL_VERSION,
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
                task_ids=has_expired_promote_pending_workflow_with_replacement.__name__,
                key=ModelDeploymentSuccessionKeys.EXPIRED_MLFLOW_RUN_ID,
            )
        )

class DeleteExpiredPromotePendingWorkflowXCom(BaseModel):
    model_config = ConfigDict(strict=False)

    expired_id: UUID

    @classmethod
    def from_context(cls, context: dict) -> "DeleteExpiredPromotePendingWorkflowXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            expired_id=ti.xcom_pull(
                task_ids=has_expired_promote_pending_workflow_with_replacement.__name__,
                key=ModelDeploymentSuccessionKeys.EXPIRED_ID,
            )
        )

class CheckCurrentModelDeploymentWorkflowDriftedXCom(BaseModel):
    model_config = ConfigDict(strict=True)

    drift_summary: dict

    @classmethod
    def from_context(cls, context: dict) -> "CheckCurrentModelDeploymentWorkflowDriftedXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            drift_summary=ti.xcom_pull(
                task_ids=has_drift.__name__,
                key=DriftMonitorKeys.DRIFT_SUMMARY,
            )
        )

class HasDriftXCom(BaseModel):
    model_config = ConfigDict(strict=True)

    drift_detected: bool
    drift_summary: dict

    @classmethod
    def from_context(cls, context: dict) -> "HasDriftXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            drift_detected=ti.xcom_pull(
                task_ids=drift_check_task_id.__name__,
                key=DriftMonitorKeys.DRIFT_DETECTED,
            ),
            drift_summary=ti.xcom_pull(
                task_ids=drift_check_task_id.__name__,
                key=DriftMonitorKeys.DRIFT_SUMMARY,
            )
        )
