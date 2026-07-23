from dataclasses import dataclass

@dataclass(frozen=True)
class MLFlowArtifactsConfig:
    reference_dataset_filename: str = "reference.parquet"
