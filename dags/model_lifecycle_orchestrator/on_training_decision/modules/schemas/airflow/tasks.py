from uuid import UUID

from pydantic import BaseModel, StrictBool, StrictStr

class ModelDeploymentWorkflowForTraining(BaseModel):
    id: UUID

class TrainingDecision(BaseModel):
    approved: StrictBool
    model_deployment_workflow: ModelDeploymentWorkflowForTraining

class ModelDeploymentWorkflowForPromotion(BaseModel):
    slack_promotion_approval_message_ts: StrictStr

