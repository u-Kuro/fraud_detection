import io

import pyarrow as pa
import pyarrow.parquet as pq
from sqlalchemy import text

from services.archiving.src.modules.configs import archiving_config
from services.archiving.src.repositories.postgres import engine
from services.archiving.src.repositories.postgres.model_deployment_workflows import get_archive_cutoff
from services.shared.modules.configs import s3_config
from services.shared import logger
from services.shared.repositories.s3 import s3_client, ensure_bucket

def archive() -> None:
    cutoff = get_archive_cutoff(engine)
    if cutoff is None:
        logger.info("No active deployed model. Nothing to archive.")
        return

    ensure_bucket(s3_config.S3_MLE_BUCKET)

    batch = 0
    total = 0

    while True:
        with engine.begin() as connection:
            rows = connection.execute(text("""
                SELECT * FROM transaction_inferences
                WHERE inference_timestamp <= :cutoff
                ORDER BY inference_timestamp
                LIMIT :limit
            """), {
                "cutoff": cutoff,
                "limit": archiving_config.BATCH_SIZE
            }).mappings().fetchall()

            if not rows: break

            batch += 1
            table = pa.Table.from_pylist([dict(r) for r in rows])
            buffer = io.BytesIO()
            pq.write_table(table, buffer)
            buffer.seek(0)

            key = (
                f"{s3_config.S3_PIPELINE_ARCHIVE_PATH}"
                f"/{cutoff.strftime("year=%Y/month=%m/day=%d")}"
                f"/batch={batch}"
                f"/data.parquet"
            )
            s3_client.upload_fileobj(
                Fileobj=buffer,
                Bucket=s3_config.S3_MLE_BUCKET,
                Key=key
            )

            request_ids = [str(row["request_id"]) for row in rows]
            connection.execute(text("""
                DELETE FROM transaction_inferences
                WHERE request_id = ANY(:request_ids::uuid[])
            """), {
                "request_ids": request_ids
            })

        total += len(rows)
        logger.info(f"Batch {batch}: {len(rows)} rows → s3://{s3_config.S3_MLE_BUCKET}/{key}")

    logger.info(f"Archiving done. Total: {total}")