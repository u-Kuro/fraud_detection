from pydantic import BaseModel, ConfigDict

class DriftConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    MAXIMUM_CURRENT_DATASET_ROWS: int = 500_000
    MINIMUM_CURRENT_DATASET_ROWS: int = 100_000
    LOOKBACK_DAYS: int = 7

drift_config = DriftConfig()