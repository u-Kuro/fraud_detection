from uuid import UUID

from airflow.sdk.types import TaskInstance
from pydantic import BaseModel, ConfigDict

from dags.controllers.slack.drift_monitor import post_cold_start_training_approval
from dags.modules.configs.airflow.drift_monitor import drift_monitor_keys_config
from dags.modules.configs.airflow.model_deployment_workflows import model_deployment_workflows_keys_config
from dags.modules.schemas.airflow import AirflowTaskContext
from dags.repositories.postgres.model_deployment_workflows import check_current_model_deployment_workflow
from dags.services.drift_monitor import check_for_drift_task_id, has_drift

class HasDriftXCom(BaseModel):
    model_config = ConfigDict(strict=False)

    drift_detected: bool
    drift_summary: dict

    @classmethod
    def from_context(cls, context: dict) -> "HasDriftXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            drift_detected=ti.xcom_pull(
                task_ids=check_for_drift_task_id.__name__,
                key=drift_monitor_keys_config.DRIFT_DETECTED_KEY,
            ),
            drift_summary=ti.xcom_pull(
                task_ids=check_for_drift_task_id.__name__,
                key=drift_monitor_keys_config.DRIFT_SUMMARY_KEY,
            )
        )

class CheckCurrentModelDeploymentWorkflowXCom(BaseModel):
    model_config = ConfigDict(strict=False)

    drift_summary: dict

    @classmethod
    def from_context(cls, context: dict) -> "CheckCurrentModelDeploymentWorkflowXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            drift_summary=ti.xcom_pull(
                task_ids=has_drift.__name__,
                key=drift_monitor_keys_config.DRIFT_SUMMARY_KEY,
            )
        )

class PostTrainingApprovalXCom(BaseModel):
    model_config = ConfigDict(strict=False)

    drift_summary: dict

    @classmethod
    def from_context(cls, context: dict) -> "PostTrainingApprovalXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            drift_summary=ti.xcom_pull(
                task_ids=check_current_model_deployment_workflow.__name__,
                key=drift_monitor_keys_config.DRIFT_SUMMARY_KEY,
            )
        )

class CreateTrainPendingWorkflowXCom(BaseModel):
    model_config = ConfigDict(strict=False)

    workflow_id: UUID
    training_approval_slack_ts: str | None

    @classmethod
    def from_context(cls, context: dict) -> "CreateTrainPendingWorkflowXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            workflow_id=ti.xcom_pull(
                task_ids=post_cold_start_training_approval.__name__,
                key=model_deployment_workflows_keys_config.MODEL_DEPLOYMENT_WORKFLOW_ID_KEY,
            ),
            training_approval_slack_ts=ti.xcom_pull(
                task_ids=post_cold_start_training_approval.__name__,
                key=model_deployment_workflows_keys_config.TRAINING_APPROVAL_SLACK_TS_KEY,
            ),
        )

class UpdateTrainingPendingWorkflowXCom(BaseModel):
    model_config = ConfigDict(strict=False)

    workflow_id: str
    training_approval_slack_ts: str
    drift_summary: dict

    @classmethod
    def from_context(cls, context: dict) -> "UpdateTrainingPendingWorkflowXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            workflow_id=ti.xcom_pull(
                task_ids=check_current_model_deployment_workflow.__name__,
                key=model_deployment_workflows_keys_config.MODEL_DEPLOYMENT_WORKFLOW_ID_KEY,
            ),
            drift_summary=ti.xcom_pull(
                task_ids=check_current_model_deployment_workflow.__name__,
                key=drift_monitor_keys_config.DRIFT_SUMMARY_KEY,
            )
        )