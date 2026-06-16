import io
from datetime import datetime

import pyarrow as pa
import pyarrow.parquet as pq
from sqlalchemy import text

from services.archiving.src.modules.environment import environment
from services.archiving.src.repositories.postgres.postgres import engine
from services.archiving.src.repositories.postgres.pipeline_state import get_archive_cutoff
from services.archiving.src.repositories.s3.s3 import s3_client
from shared.logging import logger

def _ensure_bucket(bucket: str) -> None:
    try:
        s3_client.head_bucket(Bucket=bucket)
    except Exception:
        s3_client.create_bucket(Bucket=bucket)


def _s3_key(cutoff: datetime, batch: int) -> str:
    return f"archive/{cutoff.year}/{cutoff.month:02d}/{cutoff.day:02d}/batch_{batch:04d}.parquet"


def archive() -> None:
    cutoff = get_archive_cutoff(engine)
    if cutoff is None:
        logger.info("No active deployed model. Nothing to archive.")
        return

    logger.info(f"Archiving rows with inference_timestamp <= {cutoff.isoformat()}")
    _ensure_bucket(environment.S3_MODEL_DATASETS_BUCKET)

    batch = 0
    total = 0

    while True:
        with engine.begin() as conn:
            rows = conn.execute(text("""
                SELECT * FROM transaction_inferences
                WHERE inference_timestamp <= :cutoff
                ORDER BY inference_timestamp
                LIMIT :limit
            """), {"cutoff": cutoff, "limit": environment.ARCHIVE_BATCH_SIZE}).mappings().fetchall()

            if not rows:
                break

            batch += 1
            table = pa.Table.from_pylist([dict(r) for r in rows])
            buf = io.BytesIO()
            pq.write_table(table, buf)
            buf.seek(0)

            key = _s3_key(cutoff, batch)
            s3_client.upload_fileobj(buf, environment.S3_MODEL_DATASETS_BUCKET, key)

            ids = [str(r["request_id"]) for r in rows]
            conn.execute(
                text("DELETE FROM transaction_inferences WHERE request_id = ANY(:ids)"),
                {"ids": ids},
            )

        total += len(rows)
        logger.info(f"Batch {batch}: {len(rows)} rows → s3://{environment.S3_MODEL_DATASETS_BUCKET}/{key}")

    logger.info(f"Done. Total archived: {total}")