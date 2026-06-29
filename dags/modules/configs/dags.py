from pydantic import BaseModel, ConfigDict

class DagsConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    OWNER: str = "mle"

dags_config = DagsConfig()