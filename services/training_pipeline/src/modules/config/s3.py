from pydantic import BaseModel

class S3Config(BaseModel):
    S3_PIPELINE_DATASET_REFERENCE_PATH: str = "pipeline/dataset_reference"
    S3_PIPELINE_DATASETS_PATH: str = "pipeline/datasets"

s3_config = S3Config()