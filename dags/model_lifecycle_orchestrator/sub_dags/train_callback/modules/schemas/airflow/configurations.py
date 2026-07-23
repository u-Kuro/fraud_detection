from uuid import UUID

from pydantic import BaseModel, ConfigDict

class TrainingCallbackConfigurations(BaseModel):
    model_config = ConfigDict(strict=False)

    approved: bool
    workflow_id: UUID
    for_promotion: bool

    @classmethod
    def from_context(cls, context: dict) -> "TrainingCallbackConfigurations":
        return cls(**(context["dag_run"].conf or {}))