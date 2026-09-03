from collections import defaultdict
from datetime import date

from services.archive.src.repositories.postgres.postgres import sql_session
from services.archive.src.repositories.postgres.transaction_inferences import get_transaction_inferences_batch, delete_transaction_inferences_batch
from services.archive.src.repositories.s3.archive import upload_transaction_inference_batch
from services.shared.src.modules.environment.s3 import s3_environment
from services.shared.src.repositories import ensure_bucket

def archive_transaction_inferences():
    ensure_bucket(s3_environment.S3_BUCKET_NAME)

    batch_by_date: defaultdict[date, int] = defaultdict(int)

    while True:
        with sql_session.begin() as session:
            # get existing transaction inferences to archive
            transaction_inferences: list[dict] = get_transaction_inferences_batch(session)
            if len(transaction_inferences) == 0: break

            # group transaction inferences by date
            transaction_inferences_by_date: defaultdict[date, list[dict]] = defaultdict(list[dict])
            for item in transaction_inferences:
                transaction_inferences_by_date[item["transaction_timestamp"].date()].append(item)

            for date_key in transaction_inferences_by_date:
                batch_by_date[date_key] += 1

            # archive transaction inferences to s3 by date
            upload_transaction_inference_batch(
                transaction_inferences_by_date,
                batch_by_date
            )

            # delete archived transaction inferences
            delete_transaction_inferences_batch(
                session,
                transaction_inferences
            )