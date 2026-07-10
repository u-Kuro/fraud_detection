import io
import pyarrow as pa
import pyarrow.parquet as pq
from services.shared.modules.configs import s3_config
from services.shared.repositories.s3 import s3_client, ensure_bucket

def save_permanent_dataset(
    table: pa.Table,
    model_name: str,
    model_version: int
) -> str:
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
    ensure_bucket(s3_config.S3_MLE_BUCKET)
    buffer = io.BytesIO()
    pq.write_table(table, buffer)
    buffer.seek(0)
    s3_client.upload_fileobj(
        Fileobj=buffer,
        Bucket=s3_config.S3_MLE_BUCKET,
        Key=f"{s3_config.S3_PIPELINE_FRAUD_DETECTION_DRIFT_REFERENCE}/latest.parquet",
    )
