import io
import boto3
import pyarrow as pa
import pyarrow.parquet as pq
from .environment import environment


def make_s3():
    return boto3.client(
        "s3",
        endpoint_url=environment.SEAWEEDFS_S3_URL,
        aws_access_key_id=environment.SEAWEEDFS_ACCESS_KEY,
        aws_secret_access_key=environment.SEAWEEDFS_SECRET_KEY,
    )


def _ensure(s3, bucket: str) -> None:
    try:
        s3.head_bucket(Bucket=bucket)
    except Exception:
        s3.create_bucket(Bucket=bucket)


def save_permanent_dataset(
    s3, table: pa.Table, model_name: str, model_version: int
) -> str:
    """Write the full training dataset to the permanent namespaced path. Returns S3 key."""
    _ensure(s3, environment.SEAWEEDFS_MODEL_DATASETS_BUCKET)
    key = f"{model_name}/{model_version}/dataset.parquet"
    buf = io.BytesIO()
    pq.write_table(table, buf)
    buf.seek(0)
    s3.upload_fileobj(buf, environment.SEAWEEDFS_MODEL_DATASETS_BUCKET, key)
    return key


def overwrite_reference_dataset(s3, table: pa.Table) -> None:
    """Overwrite the fixed reference path used by drift_monitor."""
    _ensure(s3, environment.SEAWEEDFS_TRAINED_MODEL_DATASET_BUCKET)
    buf = io.BytesIO()
    pq.write_table(table, buf)
    buf.seek(0)
    s3.upload_fileobj(
        buf,
        environment.SEAWEEDFS_TRAINED_MODEL_DATASET_BUCKET,
        "reference/dataset.parquet",
    )
