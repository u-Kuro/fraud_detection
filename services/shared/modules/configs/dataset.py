from dataclasses import dataclass

@dataclass(frozen=True)
class DatasetConfig:
    MAXIMUM_DATASET_ROWS: int = 500_000
    MINIMUM_ROWS: int = 100_000