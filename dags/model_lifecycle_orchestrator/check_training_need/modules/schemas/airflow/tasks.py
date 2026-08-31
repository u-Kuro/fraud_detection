from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator, StrictStr, StrictInt, StrictBool, Strict

from dags.model_lifecycle_orchestrator.check_training_need.modules.configs.airflow.data_keys import DriftCheckKeys
from dags.model_lifecycle_orchestrator.check_training_need.services.tasks import drift_check_operator
from dags.shared.modules.schemas.airflow import TaskContext

class ExpiredModelDeploymentWorkflow(BaseModel):
    workflow_id: UUID
    model_name: StrictStr
    model_version: StrictInt
    mlflow_run_id: StrictStr
    slack_promotion_approval_message_ts: StrictStr

class ReservedModelDeploymentWorkflow(BaseModel):
    model_name: StrictStr
    model_version: StrictInt

class ExpiredAndReservedModelDeploymentWorkflows(BaseModel):
    expired: ExpiredModelDeploymentWorkflow
    reserved: ReservedModelDeploymentWorkflow

class ActiveModelDeployment(BaseModel):
    mlflow_run_id: StrictStr

class DriftCheckResult(BaseModel):
    drift_detected: StrictBool
    drift_summary: Annotated[dict[StrictStr, Annotated[dict, Strict()]], Strict()]

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
    model_config = ConfigDict(validate_assignment=True)

    state: StrictStr
    workflow_id: UUID | None = None
    slack_training_approval_message_ts: StrictStr | None = None
    should_train_for_promotion: StrictBool