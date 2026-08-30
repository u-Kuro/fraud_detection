from uuid import UUID

from pydantic import BaseModel, ConfigDict

from dags.shared.modules.schemas.airflow import TaskDAGRun

class PromotionDecisionCallbackConfigurations(BaseModel):
    model_config = ConfigDict(strict=False)

    approved: bool
    workflow_id: UUID

    @classmethod
    def from_context(cls, context: dict) -> "PromotionDecisionCallbackConfigurations":
        return cls.model_validate(TaskDAGRun.from_context(context).configurations)