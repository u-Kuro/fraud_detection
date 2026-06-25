import io
import pyarrow as pa
import pyarrow.parquet as pq
from shared.configs import s3_config
from shared.s3 import s3_client, ensure_bucket

def save_permanent_dataset(
    table: pa.Table,
    model_name: str,
    model_version: int
) -> str:
    """Write the full training dataset to the permanent namespaced path. Returns S3 key."""
    ensure_bucket(s3_config.S3_MLE_BUCKET)
    key = f"{s3_config.S3_PIPELINE_DATASETS_PATH}/{model_name}/{model_version}/dataset.parquet"
    buffer = io.BytesIO()
    pq.write_table(table, buffer)
    buffer.seek(0)
    s3_client.upload_fileobj(
        Fileobj=buffer,
        Bucket=s3_config.S3_MLE_BUCKET,
        Key=key
    )
    return key

def overwrite_reference_dataset(table: pa.Table) -> None:
    """Overwrite the fixed reference path used by drift_monitor."""
    ensure_bucket(s3_config.S3_MLE_BUCKET)
    buffer = io.BytesIO()
    pq.write_table(table, buffer)
    buffer.seek(0)
    s3_client.upload_fileobj(
        Fileobj=buffer,
        Bucket=s3_config.S3_MLE_BUCKET,
        Key=f"{s3_config.S3_PIPELINE_REFERENCE_PATH}/latest.parquet",
    )
