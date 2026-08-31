from uuid import UUID

from pydantic import BaseModel, StrictBool

from dags.shared.modules.schemas.airflow import TaskDAGRun

class PromotionDecisionCallbackConfigurations(BaseModel):
    approved: StrictBool
    workflow_id: UUID

    @classmethod
    def from_context(cls, context: dict) -> "PromotionDecisionCallbackConfigurations":
        return cls.model_validate(TaskDAGRun.from_context(context).configurations)