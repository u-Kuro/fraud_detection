import io

import pyarrow.parquet as pq
import pyarrow as pa

from shared.configs import s3_config
from shared.s3 import s3

def load_reference_parquet() -> pa.Table | None:
    try:
        object = s3.get_object(
            Bucket=s3_config.S3_MLE_BUCKET,
            Key=f"{s3_config.S3_PIPELINE_DATASET_REFERENCE_PATH}/latest.parquet",
        )
        buffer = io.BytesIO(object["Body"].read())
        return pq.read_table(buffer)
    except:
        return None