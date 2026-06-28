import io

import pyarrow.parquet as pq
import pyarrow as pa

from shared.modules.configs import s3_config
from shared.repositories.s3 import s3_client

def load_reference_parquet() -> pa.Table | None:
    try:
        obj = s3_client.get_object(
            Bucket=s3_config.S3_MLE_BUCKET,
            Key=f"{s3_config.S3_PIPELINE_FRAUD_DETECTION_DRIFT_REFERENCE}/latest.parquet",
        )
        buffer = io.BytesIO(obj["Body"].read())
        return pq.read_table(buffer)
    except:
        return None