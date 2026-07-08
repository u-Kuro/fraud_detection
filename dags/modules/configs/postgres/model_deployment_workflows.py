from pydantic import BaseModel, ConfigDict


class ModelDeploymentWorkflowsConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    TRAINED_MODEL_EXPIRATION_DAYS: int = 7

model_deployment_workflows_config = ModelDeploymentWorkflowsConfig()