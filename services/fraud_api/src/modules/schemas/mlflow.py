from pydantic import BaseModel, ConfigDict

class DeployedModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    model_name: str
    model_version: int