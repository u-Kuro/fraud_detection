from pydantic import BaseModel, ConfigDict

class S3Config(BaseModel):
    model_config = ConfigDict(frozen=True)

    S3_MLE_BUCKET: str = "mle"
    S3_PIPELINE_REFERENCE_PATH: str = "pipeline/reference"
    S3_PIPELINE_DATASETS_PATH: str = "pipeline/datasets"
    S3_PIPELINE_DRIFT_REPORTS_PATH: str = "pipeline/drift-reports"

s3_config = S3Config()