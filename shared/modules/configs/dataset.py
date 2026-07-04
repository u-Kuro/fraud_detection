from pydantic import BaseModel, ConfigDict

class DatasetConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    MAXIMUM_DATASET_ROWS: int = 500_000
    MINIMUM_ROWS: int = 100_000

dataset_config = DatasetConfig()