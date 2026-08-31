from uuid import UUID

from pydantic import BaseModel, StrictBool

class TrainingValue(BaseModel):
    workflow_id: UUID
    should_train_for_promotion: StrictBool

class PromotionValue(BaseModel):
    workflow_id: UUID