from uuid import UUID

from pydantic import BaseModel, ConfigDict

class TrainingCallbackConfigurations(BaseModel):
    model_config = ConfigDict(strict=False)

    workflow_id: UUID
    approved: bool

    @classmethod
    def from_context(cls, context: dict) -> "TrainingCallbackConfigurations":
        return cls(**(context["dag_run"].conf or {}))