from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, StrictBool

class ModelDeploymentWorkflowForPromotion(BaseModel):
    id: UUID

class PromotionDecision(BaseModel):
    approved: StrictBool
    model_deployment_workflow: ModelDeploymentWorkflowForPromotion

class PromotedModelDeployment(BaseModel):
    dataset_max_timestamp: datetime