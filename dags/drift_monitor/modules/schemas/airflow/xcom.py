from uuid import UUID

from airflow.sdk.types import TaskInstance
from pydantic import BaseModel, ConfigDict

from dags.drift_monitor.controllers.slack import post_cold_start_training_approval
from dags.drift_monitor.modules.configs.airflow import DriftMonitorKeys
from dags.drift_monitor.repositories.postgres.model_deployment_workflows import check_current_model_deployment_workflow
from dags.drift_monitor.services.tasks import check_for_drift_task_id, has_drift

from dags.shared.modules.configs.airflow import ModelDeploymentWorkflowsKeys
from dags.shared.modules.schemas.airflow import AirflowTaskContext

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
                key=DriftMonitorKeys.DRIFT_DETECTED_KEY,
            ),
            drift_summary=ti.xcom_pull(
                task_ids=check_for_drift_task_id.__name__,
                key=DriftMonitorKeys.DRIFT_SUMMARY_KEY,
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
                key=DriftMonitorKeys.DRIFT_SUMMARY_KEY,
            )
        )

class PostRetrainingApprovalXCom(BaseModel):
    model_config = ConfigDict(strict=False)

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
    model_config = ConfigDict(strict=False)

    workflow_id: UUID
    training_approval_slack_ts: str | None

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
    model_config = ConfigDict(strict=False)

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