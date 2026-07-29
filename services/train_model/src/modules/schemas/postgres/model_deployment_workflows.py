from pydantic import BaseModel

class ModelDeploymentWorkflowDatasetTimestamps(BaseModel):
    model_dataset_min_iso_datetime: str
    model_dataset_max_iso_datetime: str