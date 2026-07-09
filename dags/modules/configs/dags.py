from pydantic import BaseModel, ConfigDict

class DagsConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    OWNER: str = "mle"
    ECR_REGISTRY_URL: str = "localhost:4566" # TODO - check actual url in terraform outputs

dags_config = DagsConfig()