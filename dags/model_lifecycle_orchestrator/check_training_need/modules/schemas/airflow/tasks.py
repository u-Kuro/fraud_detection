from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator

from dags.model_lifecycle_orchestrator.check_training_need.modules.configs.airflow.data_keys import DriftCheckKeys
from dags.model_lifecycle_orchestrator.check_training_need.services.tasks import drift_check_operator
from dags.shared.modules.schemas.airflow import TaskContext

class ExpiredModelDeploymentWorkflow(BaseModel):
    workflow_id: UUID
    model_name: str
    model_version: int
    mlflow_run_id: str
    promotion_approval_slack_ts: str

class ReservedModelDeploymentWorkflow(BaseModel):
    model_name: str
    model_version: int

class ExpiredModelDeploymentWorkflowWithItsReplacement(BaseModel):
    model_config = ConfigDict(strict=False)

    expired: ExpiredModelDeploymentWorkflow
    reserved: ReservedModelDeploymentWorkflow

class ActiveModelDeployment(BaseModel):
    model_config = ConfigDict(strict=True)

    mlflow_run_id: str

class DriftCheckResult(BaseModel):
    model_config = ConfigDict(strict=True)

    drift_detected: bool
    drift_summary: dict[str, dict]

    @model_validator(mode="wrap")
    @classmethod
    def xcom_parse(cls, context: TaskContext) -> "DriftCheckResult":
        task_instance = context.task_instance
        task_id = context.resolve_task_id(drift_check_operator.__name__)
        return cls(
            drift_detected=task_instance.xcom_pull(
                task_ids=task_id,
                key=DriftCheckKeys.DRIFT_DETECTED,
            ),
            drift_summary=task_instance.xcom_pull(
                task_ids=task_id,
                key=DriftCheckKeys.DRIFT_SUMMARY
            ),
        )

class ModelDeploymentWorkflowForTraining(BaseModel):
    model_config = ConfigDict(
        strict=False,
        validate_assignment = True
    )

    state: str
    workflow_id: UUID | None = None
    training_approval_slack_ts: str | None = None
    should_train_for_promotion: bool