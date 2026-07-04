from pydantic import BaseModel, ConfigDict

class EvidentlyConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    DATA_DRIFT_KEY: str = "data_drift"
    CONCEPT_DRIFT_KEY: str = "concept_drift"
    DRIFTED_KEY: str = "drifted"

evidently_config = EvidentlyConfig()