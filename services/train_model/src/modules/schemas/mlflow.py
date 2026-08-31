from pydantic import BaseModel, StrictStr, StrictInt

class MLFlowRegisteredModelInfo(BaseModel):
    run_id: StrictStr
    model_id: StrictStr
    model_name: StrictStr
    model_version: StrictInt