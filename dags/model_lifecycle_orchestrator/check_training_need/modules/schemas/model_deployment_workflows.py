from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, StrictStr, Strict

from dags.shared.modules.schemas.postgres.model_deployment_workflows import ModelDeploymentWorkflowState

class ModelDeploymentWorkflow(BaseModel):
    id: UUID
    state: Annotated[ModelDeploymentWorkflowState, Strict()]
    slack_training_approval_message_ts: StrictStr

    @classmethod
    def model_field_keys(cls, rename: dict[str, str] | None = None) -> list[str]:
        keys: list[str] = list(cls.model_fields.keys())
        if rename: return [str(rename.get(key, key)) for key in keys]
        return keys