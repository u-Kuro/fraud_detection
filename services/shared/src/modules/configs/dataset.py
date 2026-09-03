from dataclasses import dataclass

@dataclass(frozen=True)
class DatasetConfig:
    maximum_dataset_rows: int = 500_000
    minimum_rows: int = 100_000