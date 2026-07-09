from pydantic import BaseModel, ConfigDict

class ModelDeploymentWorkflowsKeysConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    MODEL_DEPLOYMENT_WORKFLOW_ID_KEY: str = "MODEL_DEPLOYMENT_WORKFLOW_ID"
    TRAINING_APPROVAL_SLACK_TS_KEY: str = "TRAINING_APPROVAL_SLACK_TS"

model_deployment_workflows_keys_config = ModelDeploymentWorkflowsKeysConfig()