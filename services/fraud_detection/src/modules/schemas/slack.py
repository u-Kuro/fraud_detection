from uuid import UUID

from pydantic import BaseModel, StrictBool, ConfigDict

class TrainingValue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workflow_id: UUID
    should_train_for_promotion: StrictBool

class PromotionValue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workflow_id: UUID