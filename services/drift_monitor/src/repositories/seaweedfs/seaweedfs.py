import io
from datetime import datetime, timezone

import boto3
import pyarrow.parquet as pq
import pyarrow as pa
from mypy_boto3_s3.client import S3Client

from services.drift_monitor.src.modules.environment import environment

s3: S3Client = boto3.client(
    "s3",
    endpoint_url=environment.SEAWEEDFS_S3_URL,
    aws_access_key_id=environment.SEAWEEDFS_ACCESS_KEY,
    aws_secret_access_key=environment.SEAWEEDFS_SECRET_KEY,
)

def ensure_bucket(bucket: str) -> None:
    try: s3.head_bucket(Bucket=bucket)
    except: s3.create_bucket(Bucket=bucket)

def load_reference_parquet() -> pa.Table | None:
    """Return the reference dataset table, or None if it does not exist yet."""
    try:
        object = s3.get_object(
            Bucket=environment.SEAWEEDFS_TRAINED_MODEL_DATASET_BUCKET,
            Key="reference/dataset.parquet",
        )
        buffer = io.BytesIO(object["Body"].read())
        return pq.read_table(buffer)
    except s3.exceptions.NoSuchKey:
        return None
    except:
        return None

def upload_drift_report(html_bytes: bytes, json_bytes: bytes) -> None:
    ensure_bucket(environment.SEAWEEDFS_DRIFT_REPORTS_BUCKET)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_drift_report"
    s3.upload_fileobj(
        Fileobj=io.BytesIO(html_bytes),
        Bucket=environment.SEAWEEDFS_DRIFT_REPORTS_BUCKET,
        Key=f"{filename}.html",
    )
    s3.put_object(
        Bucket=environment.SEAWEEDFS_DRIFT_REPORTS_BUCKET,
        Key=f"{filename}.json",
        Body=json_bytes,
        ContentType="application/json",
    )