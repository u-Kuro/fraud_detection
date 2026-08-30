from uuid import UUID

from pydantic import BaseModel, ConfigDict

class TrainingValue(BaseModel):
    model_config = ConfigDict(strict=False)

    workflow_id: UUID
    should_train_for_promotion: bool

class PromotionValue(BaseModel):
    model_config = ConfigDict(strict=False)

    workflow_id: UUID