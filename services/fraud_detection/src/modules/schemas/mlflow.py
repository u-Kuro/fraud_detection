from pydantic import BaseModel, ConfigDict, StrictStr, StrictInt

class DeployedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model_name: StrictStr
    model_version: StrictInt