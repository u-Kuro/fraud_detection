from uuid import UUID

from pydantic import BaseModel, ConfigDict

from dags.shared.modules.schemas.airflow import TaskDAGRun

class TrainingDecisionCallbackConfigurations(BaseModel):
    model_config = ConfigDict(strict=False)

    approved: bool
    workflow_id: UUID
    should_train_for_promotion: bool

    @classmethod
    def from_context(cls, context: dict) -> "TrainingDecisionCallbackConfigurations":
        return cls.model_validate(TaskDAGRun.from_context(context).configurations)