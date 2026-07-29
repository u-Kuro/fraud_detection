import io
from collections import defaultdict
from datetime import date

import pyarrow as pa
import pyarrow.parquet as pq

from services.shared.modules.configs.s3 import S3Config
from services.shared.repositories.s3.s3 import s3_client

def upload_transaction_inference_batch(
    transaction_inferences_by_date: defaultdict[date, list[dict]],
    batch_by_date: defaultdict[date, int]
):
    for date_key, item in transaction_inferences_by_date.items():
        buffer = io.BytesIO()
        pq.write_table(
            pa.Table.from_pylist(mapping=item),
            buffer
        )
        buffer.seek(0)

        s3_client.upload_fileobj(
            Fileobj=buffer,
            Bucket=S3Config.S3_MLE_BUCKET,
            Key=(
                f"{S3Config.S3_PIPELINE_ARCHIVE_PATH}"
                f"/year={date_key.year}/month={date_key.month:02d}/day={date_key.day:02d}"
                f"/batch={batch_by_date[date_key]}/data.parquet"
            ),
        )