from pydantic import BaseModel, ConfigDict

class EvidentlyConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    data_drift_key: str = "data_drift"
    concept_drift_key: str = "concept_drift"
    drifted_key: str = "drifted"

evidently_config = EvidentlyConfig()