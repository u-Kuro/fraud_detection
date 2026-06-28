from pydantic import BaseModel, ConfigDict

class DagsConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    OWNER: str = "mle"
    S3_PIPELINE_FRAUD_DETECTION_DRIFT_REFERENCE: str = "pipeline/fraud-detection/drift/reference"
    S3_PIPELINE_DATASETS_PATH: str = "pipeline/fraud-detection/models"
    S3_PIPELINE_DRIFT_REPORTS_PATH: str = "pipeline/fraud-detection/drift/reports"
    S3_PIPELINE_ARCHIVE_PATH: str = "pipeline/fraud-detection/archive"

dags_config = DagsConfig()