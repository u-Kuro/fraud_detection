from pydantic import BaseModel#, ConfigDict

class MLFlowRegisteredModelInfo(BaseModel):
    run_id: str
    model_id: str
    model_name: str
    model_version: int