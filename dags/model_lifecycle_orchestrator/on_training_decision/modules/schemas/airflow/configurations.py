from uuid import UUID

from pydantic import BaseModel, StrictBool

from dags.shared.modules.schemas.airflow import TaskDAGRun

class TrainingDecisionCallbackConfigurations(BaseModel):
    approved: StrictBool
    workflow_id: UUID
    should_train_for_promotion: StrictBool

    @classmethod
    def from_context(cls, context: dict) -> "TrainingDecisionCallbackConfigurations":
        return cls.model_validate(TaskDAGRun.from_context(context).configurations)