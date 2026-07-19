from uuid import UUID

from airflow.sdk.types import TaskInstance
from pydantic import BaseModel, ConfigDict

from dags.model_lifecycle_orchestrator.controllers.slack import post_cold_start_training_approval
from dags.model_lifecycle_orchestrator.modules.configs.airflow import DriftMonitorKeys
from dags.model_lifecycle_orchestrator.repositories.mlflow.registered_model import replace_expired_model, delete_expired_model
from dags.model_lifecycle_orchestrator.repositories.postgres.model_deployment_workflows import check_current_model_deployment_workflow, has_expired_promote_pending_workflow_with_replacement
from dags.model_lifecycle_orchestrator.services.tasks import drift_check_task_id, has_drift

from dags.shared.modules.configs.airflow import ModelDeploymentWorkflowsKeys
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
                key=DriftMonitorKeys.DRIFT_DETECTED_KEY,
            ),
            drift_summary=ti.xcom_pull(
                task_ids=drift_check_task_id.__name__,
                key=DriftMonitorKeys.DRIFT_SUMMARY_KEY,
            )
        )

class CheckCurrentModelDeploymentWorkflowXCom(BaseModel):
    model_config = ConfigDict(strict=True)

    drift_summary: dict

    @classmethod
    def from_context(cls, context: dict) -> "CheckCurrentModelDeploymentWorkflowXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            drift_summary=ti.xcom_pull(
                task_ids=has_drift.__name__,
                key=DriftMonitorKeys.DRIFT_SUMMARY_KEY,
            )
        )

class PostRetrainingApprovalXCom(BaseModel):
    model_config = ConfigDict(strict=True)

    drift_summary: dict

    @classmethod
    def from_context(cls, context: dict) -> "PostRetrainingApprovalXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            drift_summary=ti.xcom_pull(
                task_ids=check_current_model_deployment_workflow.__name__,
                key=DriftMonitorKeys.DRIFT_SUMMARY_KEY,
            )
        )

class CreateTrainPendingWorkflowXCom(BaseModel):
    model_config = ConfigDict(strict=True)

    workflow_id: UUID
    training_approval_slack_ts: str

    @classmethod
    def from_context(cls, context: dict) -> "CreateTrainPendingWorkflowXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            workflow_id=ti.xcom_pull(
                task_ids=post_cold_start_training_approval.__name__,
                key=ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID_KEY,
            ),
            training_approval_slack_ts=ti.xcom_pull(
                task_ids=post_cold_start_training_approval.__name__,
                key=ModelDeploymentWorkflowsKeys.TRAINING_APPROVAL_SLACK_TS_KEY,
            ),
        )

class UpdateRetrainingPendingWorkflowXCom(BaseModel):
    model_config = ConfigDict(strict=True)

    workflow_id: str
    training_approval_slack_ts: str
    drift_summary: dict

    @classmethod
    def from_context(cls, context: dict) -> "UpdateRetrainingPendingWorkflowXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            workflow_id=ti.xcom_pull(
                task_ids=check_current_model_deployment_workflow.__name__,
                key=ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID_KEY,
            ),
            training_approval_slack_ts=ti.xcom_pull(
                task_ids=check_current_model_deployment_workflow.__name__,
                key=ModelDeploymentWorkflowsKeys.TRAINING_APPROVAL_SLACK_TS_KEY,
            ),
            drift_summary=ti.xcom_pull(
                task_ids=check_current_model_deployment_workflow.__name__,
                key=DriftMonitorKeys.DRIFT_SUMMARY_KEY,
            )
        )