import io
from datetime import datetime, timezone

from services.shared.modules.configs import S3Config
from services.shared.repositories.s3 import s3_client, ensure_bucket

def upload_drift_report(html_bytes: bytes, json_bytes: bytes) -> None:
    ensure_bucket(S3Config.S3_MLE_BUCKET)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    s3_client.upload_fileobj(
        Fileobj=io.BytesIO(html_bytes),
        Bucket=S3Config.S3_MLE_BUCKET,
        Key=f"{S3Config.S3_PIPELINE_DRIFT_REPORTS_PATH}/{timestamp}.html",
    )
    s3_client.put_object(
        Bucket=S3Config.S3_MLE_BUCKET,
        Key=f"{S3Config.S3_PIPELINE_DRIFT_REPORTS_PATH}/{timestamp}.json",
        Body=json_bytes,
        ContentType="application/json",
    )