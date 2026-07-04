from pydantic import BaseModel, ConfigDict

class DagsConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    OWNER: str = "mle"
    MODEL_DEPLOYMENT_WORKFLOW_ID_KEY: str = "MODEL_DEPLOYMENT_WORKFLOW_ID"

dags_config = DagsConfig()