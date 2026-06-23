import io
from datetime import datetime, timezone

import pyarrow.parquet as pq
import pyarrow as pa

from services.drift_monitor.src.modules.environment import environment
from shared.s3 import s3, ensure_bucket

def load_reference_parquet() -> pa.Table | None:
    try:
        object = s3.get_object(
            Bucket=environment.S3_MLE_BUCKET,
            Key=f"{environment.S3_PIPELINE_REFERENCE_PATH}/latest.parquet",
        )
        buffer = io.BytesIO(object["Body"].read())
        return pq.read_table(buffer)
    except:
        return None

def upload_drift_report(html_bytes: bytes, json_bytes: bytes) -> None:
    ensure_bucket(environment.S3_MLE_BUCKET)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    s3.upload_fileobj(
        Fileobj=io.BytesIO(html_bytes),
        Bucket=environment.S3_MLE_BUCKET,
        Key=f"{environment.S3_PIPELINE_DRIFT_REPORTS_PATH}/{timestamp}.html",
    )
    s3.put_object(
        Bucket=environment.S3_MLE_BUCKET,
        Key=f"{environment.S3_PIPELINE_DRIFT_REPORTS_PATH}/{timestamp}.json",
        Body=json_bytes,
        ContentType="application/json",
    )