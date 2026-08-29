import io
from datetime import datetime, timezone

from services.shared.modules.configs.s3 import S3Config
from services.shared.repositories.s3.bucket import ensure_bucket
from services.shared.repositories.s3.s3 import s3_client

def upload_drift_report(html_bytes: bytes, json_bytes: bytes) -> None:
    ensure_bucket(S3Config.S3_MLE_BUCKET)

    partition = datetime.now(timezone.utc).strftime("year=%Y/month=%m/day=%d")
    s3_client.upload_fileobj(
        Fileobj=io.BytesIO(html_bytes),
        Bucket=S3Config.S3_MLE_BUCKET,
        Key=f"{S3Config.model_drift_path}/{partition}.html",
    )
    s3_client.put_object(
        Bucket=S3Config.S3_MLE_BUCKET,
        Key=f"{S3Config.model_drift_path}/{partition}.json",
        Body=json_bytes,
        ContentType="application/json",
    )