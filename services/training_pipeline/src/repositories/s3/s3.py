import io
import boto3
import pyarrow as pa
import pyarrow.parquet as pq
from mypy_boto3_s3.client import S3Client
from services.training_pipeline.src.modules.environment import environment

s3: S3Client = boto3.client(
    "s3",
    endpoint_url=environment.S3_ENDPOINT_URL,
    aws_access_key_id=environment.S3_ACCESS_KEY,
    aws_secret_access_key=environment.S3_SECRET_KEY,
)

def ensure_bucket(bucket: str) -> None:
    try: s3.head_bucket(Bucket=bucket)
    except: s3.create_bucket(Bucket=bucket)

def save_permanent_dataset(
    table: pa.Table,
    model_name: str,
    model_version: int
) -> str:
    """Write the full training dataset to the permanent namespaced path. Returns S3 key."""
    ensure_bucket(environment.S3_MLE_BUCKET)
    key = f"{environment.S3_PIPELINE_DATASETS_PATH}/{model_name}/{model_version}/dataset.parquet"
    buffer = io.BytesIO()
    pq.write_table(table, buffer)
    buffer.seek(0)
    s3.upload_fileobj(
        Fileobj=buffer,
        Bucket=environment.S3_MLE_BUCKET,
        Key=key
    )
    return key

def overwrite_reference_dataset(table: pa.Table) -> None:
    """Overwrite the fixed reference path used by drift_monitor."""
    ensure_bucket(environment.S3_MLE_BUCKET)
    buffer = io.BytesIO()
    pq.write_table(table, buffer)
    buffer.seek(0)
    s3.upload_fileobj(
        Fileobj=buffer,
        Bucket=environment.S3_MLE_BUCKET,
        Key=f"{environment.S3_PIPELINE_REFERENCE_PATH}/latest.parquet",
    )
