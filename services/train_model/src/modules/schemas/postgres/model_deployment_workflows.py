from pydantic import BaseModel, StrictStr

class ModelDeploymentWorkflowDatasetTimestamps(BaseModel):
    model_dataset_min_iso_datetime: StrictStr
    model_dataset_max_iso_datetime: StrictStr