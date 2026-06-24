import io
from datetime import datetime, timezone

from shared.configs import s3_config
from shared.s3 import s3, ensure_bucket

def upload_drift_report(html_bytes: bytes, json_bytes: bytes) -> None:
    ensure_bucket(s3_config.S3_MLE_BUCKET)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    s3.upload_fileobj(
        Fileobj=io.BytesIO(html_bytes),
        Bucket=s3_config.S3_MLE_BUCKET,
        Key=f"{s3_config.S3_PIPELINE_DRIFT_REPORTS_PATH}/{timestamp}.html",
    )
    s3.put_object(
        Bucket=s3_config.S3_MLE_BUCKET,
        Key=f"{s3_config.S3_PIPELINE_DRIFT_REPORTS_PATH}/{timestamp}.json",
        Body=json_bytes,
        ContentType="application/json",
    )