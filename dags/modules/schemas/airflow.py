from uuid import UUID

from airflow.sdk.types import TaskInstance
from pydantic import BaseModel, ConfigDict

class AirflowTaskContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    ti: TaskInstance

    @classmethod
    def from_context(cls, context: dict) -> "AirflowTaskContext":
        return cls(ti=context["ti"])

class TrainingCallbackConfigurations(BaseModel):
    model_config = ConfigDict(strict=False)

    workflow_id: UUID
    approved: bool

    @classmethod
    def from_context(cls, context: dict) -> "TrainingCallbackConfigurations":
        return cls(**(context["dag_run"].conf or {}))

class CreateTrainPendingWorkflowConfigurations(BaseModel):
    model_config = ConfigDict(strict=False)

    workflow_id: UUID
    training_approval_slack_ts: str | None

    @classmethod
    def from_context(cls, context: dict) -> "CreateTrainPendingWorkflowConfigurations":
        return cls(**(context["dag_run"].conf or {}))

class TrainingPipelineConfigurations(BaseModel):
    model_config = ConfigDict(strict=True)

    model_deployment_workflow_id: str

    @classmethod
    def from_context(cls, context: dict) -> "TrainingPipelineConfigurations":
        return cls(**(context["dag_run"].conf or {}))


class PromotionCallbackConfigurations(BaseModel):
    model_config = ConfigDict(strict=False)

    workflow_id: UUID
    approved: bool

    @classmethod
    def from_context(cls, context: dict) -> "PromotionCallbackConfigurations":
        return cls(**(context["dag_run"].conf or {}))

class PromotionPipelineConfigurations(BaseModel):
    model_config = ConfigDict(strict=True)

    model_deployment_workflow_id: str

    @classmethod
    def from_context(cls, context: dict) -> "PromotionPipelineConfigurations":
        return cls(**(context["dag_run"].conf or {}))