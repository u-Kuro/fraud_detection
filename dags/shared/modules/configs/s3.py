from dataclasses import dataclass


@dataclass(frozen=True)
class S3Config:
    S3_CONNECTION_ID: str = "mle_s3"

    S3_MLE_BUCKET: str = "mle"
    S3_PIPELINE_FRAUD_DETECTION_DRIFT_REFERENCE: str = "pipeline/fraud-detection/drift/reference"
    S3_PIPELINE_DATASETS_PATH: str = "pipeline/fraud-detection/models"
    S3_PIPELINE_DRIFT_REPORTS_PATH: str = "pipeline/fraud-detection/drift/reports"
    S3_PIPELINE_ARCHIVE_PATH: str = "pipeline/fraud-detection/archive"