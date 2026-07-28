from uuid import UUID

from airflow.sdk.types import TaskInstance
from pydantic import BaseModel, ConfigDict

from dags.model_lifecycle_orchestrator.check_training_need.controllers.slack import initialize_training_approval
from dags.model_lifecycle_orchestrator.check_training_need.modules.configs.airflow.data_keys import DriftCheckKeys, ModelDeploymentSuccessionKeys
from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.airflow.branches import DispatchTrainingApprovalBranches, SetupTrainingApprovalBranches
from dags.model_lifecycle_orchestrator.check_training_need.repositories.postgres.model_deployment_workflows import has_expired_promote_pending_workflow_with_replacement, check_current_model_deployment_workflows, initialize_train_pending_workflow
from dags.model_lifecycle_orchestrator.check_training_need.services.tasks import invalidate_expired_challenger_model, drift_check, dispatch_training_approval, setup_training_approval
from dags.shared.modules.configs.airflow.data_keys import ModelDeploymentWorkflowsKeys
from dags.shared.modules.schemas.airflow import AirflowTaskContext
from dags.shared.modules.utilities.airflow.xcom import build_task_id, xcom_pull_coalesce

class InvalidateExpiredPromotionApprovalXCom(BaseModel):
    model_config = ConfigDict(strict=True)

    promotion_approval_slack_ts: str

    @classmethod
    def from_context(cls, context: dict) -> "InvalidateExpiredPromotionApprovalXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            promotion_approval_slack_ts=ti.xcom_pull(
                task_ids=build_task_id((
                    invalidate_expired_challenger_model.__name__,
                    has_expired_promote_pending_workflow_with_replacement.__name__
                )),
                key=ModelDeploymentSuccessionKeys.REPLACEMENT_MODEL_NAME,
            )
        )

class ReplaceExpiredModelXCom(BaseModel):
    model_config = ConfigDict(strict=True)

    replacement_model_name: str
    replacement_model_version: int

    @classmethod
    def from_context(cls, context: dict) -> "ReplaceExpiredModelXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            replacement_model_name=ti.xcom_pull(
                task_ids=build_task_id((
                    invalidate_expired_challenger_model.__name__,
                    has_expired_promote_pending_workflow_with_replacement.__name__
                )),
                key=ModelDeploymentSuccessionKeys.REPLACEMENT_MODEL_NAME,
            ),
            replacement_model_version=ti.xcom_pull(
                task_ids=build_task_id((
                    invalidate_expired_challenger_model.__name__,
                    has_expired_promote_pending_workflow_with_replacement.__name__
                )),
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
                task_ids=build_task_id((
                    invalidate_expired_challenger_model.__name__,
                    has_expired_promote_pending_workflow_with_replacement.__name__
                )),
                key=ModelDeploymentSuccessionKeys.EXPIRED_MODEL_NAME,
            ),
            expired_model_version=ti.xcom_pull(
                task_ids=build_task_id((
                    invalidate_expired_challenger_model.__name__,
                    has_expired_promote_pending_workflow_with_replacement.__name__
                )),
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
                task_ids=build_task_id((
                    invalidate_expired_challenger_model.__name__,
                    has_expired_promote_pending_workflow_with_replacement.__name__
                )),
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
                task_ids=build_task_id((
                    invalidate_expired_challenger_model.__name__,
                    has_expired_promote_pending_workflow_with_replacement.__name__
                )),
                key=ModelDeploymentSuccessionKeys.EXPIRED_ID,
            )
        )

class InvalidateOldTrainingApprovalXCom(BaseModel):
    model_config = ConfigDict(strict=True)

    drift_detected: bool
    training_approval_slack_ts: str

    @classmethod
    def from_context(cls, context: dict) -> "InvalidateOldTrainingApprovalXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            drift_detected=ti.xcom_pull(
                task_ids=drift_check.__name__,
                key=DriftCheckKeys.DRIFT_DETECTED,
            ),
            training_approval_slack_ts=xcom_pull_coalesce(
                ti=ti,
                task_id_segments=(
                    dispatch_training_approval.__name__,
                    DispatchTrainingApprovalBranches,
                    check_current_model_deployment_workflows.__name__
                ),
                key=ModelDeploymentWorkflowsKeys.TRAINING_APPROVAL_SLACK_TS,
            )
        )

class ReinitializeTrainPendingWorkflow(BaseModel):
    model_config = ConfigDict(strict=False)

    workflow_id: UUID

    @classmethod
    def from_context(cls, context: dict) -> "ReinitializeTrainPendingWorkflow":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            workflow_id=xcom_pull_coalesce(
                ti=ti,
                task_id_segments=(
                    dispatch_training_approval.__name__,
                    DispatchTrainingApprovalBranches,
                    check_current_model_deployment_workflows.__name__
                ),
                key=ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID,
            )
        )

class InitializeTrainingApprovalXCom(BaseModel):
    model_config = ConfigDict(strict=False)

    workflow_id: UUID
    drift_summary: dict[str, dict] | None

    @classmethod
    def from_context(cls, context: dict) -> "InitializeTrainingApprovalXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            workflow_id=xcom_pull_coalesce(
                ti=ti,
                task_id_segments=(
                    dispatch_training_approval.__name__,
                    DispatchTrainingApprovalBranches,
                    {
                        check_current_model_deployment_workflows.__name__,
                        initialize_train_pending_workflow.__name__
                    }
                ),
                key=ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID,
            ),
            drift_summary=ti.xcom_pull(
                task_ids=drift_check.__name__,
                key=DriftCheckKeys.DRIFT_SUMMARY,
            )
        )

class UpdateTrainPendingWorkflow(BaseModel):
    model_config = ConfigDict(strict=False)

    workflow_id: UUID
    training_approval_slack_ts: str

    @classmethod
    def from_context(cls, context: dict) -> "UpdateTrainPendingWorkflow":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            workflow_id=xcom_pull_coalesce(
                ti=ti,
                task_id_segments=(
                    dispatch_training_approval.__name__,
                    DispatchTrainingApprovalBranches,
                    {
                        check_current_model_deployment_workflows.__name__,
                        initialize_train_pending_workflow.__name__
                    }
                ),
                key=ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID,
            ),
            training_approval_slack_ts=xcom_pull_coalesce(
                ti=ti,
                task_id_segments=(
                    dispatch_training_approval.__name__,
                    DispatchTrainingApprovalBranches,
                    setup_training_approval.__name__,
                    SetupTrainingApprovalBranches,
                    initialize_training_approval.__name__
                ),
                key=ModelDeploymentWorkflowsKeys.TRAINING_APPROVAL_SLACK_TS,
            )
        )

class UpdateTrainingApproval(BaseModel):
    model_config = ConfigDict(strict=False)

    workflow_id: UUID
    training_approval_slack_ts: str
    drift_summary: dict[str, dict] | None
    for_promotion: bool

    @classmethod
    def from_context(cls, context: dict) -> "UpdateTrainingApproval":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            workflow_id=xcom_pull_coalesce(
                ti=ti,
                task_id_segments=(
                    dispatch_training_approval.__name__,
                    DispatchTrainingApprovalBranches,
                    {
                        check_current_model_deployment_workflows.__name__,
                        initialize_train_pending_workflow.__name__
                    }
                ),
                key=ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID,
            ),
            training_approval_slack_ts=xcom_pull_coalesce(
                ti=ti,
                task_id_segments=(
                    dispatch_training_approval.__name__,
                    DispatchTrainingApprovalBranches,
                    setup_training_approval.__name__,
                    SetupTrainingApprovalBranches,
                    initialize_training_approval.__name__
                ),
                key=ModelDeploymentWorkflowsKeys.TRAINING_APPROVAL_SLACK_TS,
            ),
            drift_summary=ti.xcom_pull(
                task_ids=drift_check.__name__,
                key=DriftCheckKeys.DRIFT_SUMMARY,
            ),
            for_promotion=xcom_pull_coalesce(
                ti=ti,
                task_id_segments=(
                    dispatch_training_approval.__name__,
                    DispatchTrainingApprovalBranches,
                    check_current_model_deployment_workflows.__name__
                ),
                key=ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID,
            )
        )

class HasDriftXCom(BaseModel):
    model_config = ConfigDict(strict=True)

    drift_detected: bool

    @classmethod
    def from_context(cls, context: dict) -> "HasDriftXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            drift_detected=ti.xcom_pull(
                task_ids=drift_check.__name__,
                key=DriftCheckKeys.DRIFT_DETECTED,
            )
        )
