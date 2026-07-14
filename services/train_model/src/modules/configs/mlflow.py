from pydantic import BaseModel, ConfigDict, computed_field

class MLFlowArtifactsConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    reference_dataset_filename: str = "reference.parquet"

mlflow_artifacts_config = MLFlowArtifactsConfig()