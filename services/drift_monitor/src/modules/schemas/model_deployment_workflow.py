from uuid import UUID

from pydantic import BaseModel, ConfigDict

from shared.modules.schemas import ModelDeploymentWorkflowState

class ModelDeploymentWorkflow(BaseModel):
    model_config = ConfigDict(strict=False)
    
    id: UUID
    state: ModelDeploymentWorkflowState
    training_approved: bool
    training_approval_slack_ts: str

    @classmethod
    def model_field_keys(cls, rename: dict[str, str] | None = None) -> list[str]:
        keys: list[str] = list(cls.model_fields.keys())
        if rename: return [str(rename.get(key, key)) for key in keys]
        return keys