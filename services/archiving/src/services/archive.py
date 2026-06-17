import io
from datetime import datetime

import pyarrow as pa
import pyarrow.parquet as pq
from sqlalchemy import text

from services.archiving.src.modules.environment import environment
from services.archiving.src.repositories.postgres import engine
from services.archiving.src.repositories.postgres.pipeline_state import get_archive_cutoff
from services.archiving.src.repositories.s3 import s3_client
from shared.logging import logger

def ensure_bucket(bucket: str) -> None:
    try: s3_client.head_bucket(Bucket=bucket)
    except: s3_client.create_bucket(Bucket=bucket)

def s3_key(cutoff: datetime, batch: int) -> str:
    return f"archive/{cutoff.year}/{cutoff.month:02d}/{cutoff.day:02d}/batch_{batch:04d}.parquet"

def archive() -> None:
    cutoff = get_archive_cutoff(engine)
    if cutoff is None:
        logger.info("No active deployed model. Nothing to archive.")
        return

    ensure_bucket(environment.S3_MLE_BUCKET)

    batch = 0
    total = 0

    while True:
        with engine.begin() as conn:
            rows = conn.execute(text("""
                SELECT * FROM transaction_inferences
                WHERE inference_timestamp <= :cutoff
                ORDER BY inference_timestamp
                LIMIT :limit
            """), {
                "cutoff": cutoff,
                "limit": environment.ARCHIVE_BATCH_SIZE
            }).mappings().fetchall()

            if not rows:
                break

            batch += 1
            table = pa.Table.from_pylist([dict(r) for r in rows])
            buffer = io.BytesIO()
            pq.write_table(table, buffer)
            buffer.seek(0)

            s3_client.upload_fileobj(
                Fileobj=buffer,
                Bucket=environment.S3_MLE_BUCKET,
                Key=(
                    f"{environment.S3_PIPELINE_ARCHIVE_PATH}"
                    f"/{cutoff.strftime("year=%Y/month=%m/day=%d")}"
                    f"/batch={batch}"
                    f"/data.parquet"
                )
            )

            ids = [str(r["request_id"]) for r in rows]
            conn.execute(text("""
                DELETE FROM transaction_inferences
                WHERE request_id = ANY(:ids::uuid[])
            """), {
                "ids": ids
            })

        total += len(rows)