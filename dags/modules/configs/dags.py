from pydantic import BaseModel, ConfigDict

class DagsConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    OWNER: str = "mle"
    ECR_REGISTRY_URL: str = "localhost:4566" # TODO - check actual url in terraform outputs

    MODEL_DEPLOYMENT_WORKFLOW_ID_KEY: str = "MODEL_DEPLOYMENT_WORKFLOW_ID"
    TRAINING_APPROVAL_SLACK_TS_KEY: str = "TRAINING_APPROVAL_SLACK_TS"

dags_config = DagsConfig()