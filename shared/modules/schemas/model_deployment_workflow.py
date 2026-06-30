from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

class ModelDeploymentWorkflowState(str, Enum):
    train_pending = "train_pending"
    promote_pending = "promote_pending"

class ModelDeploymentWorkflow(BaseModel):
    model_config = ConfigDict(strict=False)
    id: UUID
    state: ModelDeploymentWorkflowState
    training_approved: bool
    training_approval_slack_ts: str

    @classmethod
    def model_field_keys(cls) -> list[str]:
        return list(cls.model_fields.keys())