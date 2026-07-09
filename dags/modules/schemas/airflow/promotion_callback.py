from uuid import UUID

from pydantic import BaseModel, ConfigDict

class PromotionCallbackConfigurations(BaseModel):
    model_config = ConfigDict(strict=False)

    workflow_id: UUID
    approved: bool

    @classmethod
    def from_context(cls, context: dict) -> "PromotionCallbackConfigurations":
        return cls(**(context["dag_run"].conf or {}))