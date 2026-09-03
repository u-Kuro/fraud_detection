import io
from collections import defaultdict
from datetime import date

import pandas
import pyarrow
from pyarrow import parquet

from services.shared.src.modules.configs.s3 import S3Config
from services.shared.src.modules.environment.s3 import s3_environment
from services.shared.src.repositories.s3.s3 import s3_client

def upload_transaction_inference_batch(
    transaction_inferences_by_date: defaultdict[date, list[dict]],
    batch_by_date: defaultdict[date, int]
):
    for date_key, item in transaction_inferences_by_date.items():
        buffer = io.BytesIO()
        parquet.write_table(
            table=pyarrow.Table.from_pandas(
                df=pandas.DataFrame(item),
                preserve_index=False
            ),
            where=buffer
        )
        buffer.seek(0)

        partition = date_key.strftime("year=%Y/month=%m/day=%d")
        s3_client.upload_fileobj(
            Fileobj=buffer,
            Bucket=s3_environment.S3_BUCKET_NAME,
            Key=f"{S3Config.transaction_inferences_archive_path}/{partition}/part-{batch_by_date[date_key]:04d}.parquet",
        )