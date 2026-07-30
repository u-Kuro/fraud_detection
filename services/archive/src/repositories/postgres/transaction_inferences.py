from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from services.archive.src.modules.configs.archive import ArchiveConfig
from services.archive.src.modules.environment.archive import archive_environment
from services.shared.modules.schemas.postgres.transaction_inferences import TransactionInferences

def get_transaction_inferences_batch(session: Session) -> list[dict]:
    result = session.execute(
        select(TransactionInferences.__table__)
        .where(TransactionInferences.transaction_timestamp <= archive_environment.TRANSACTION_INFERENCES_ARCHIVE_CUTOFF_ISO_DATETIME)
        .order_by(
            TransactionInferences.transaction_timestamp.asc(),
            TransactionInferences.id.asc()
        )
        .limit(ArchiveConfig.batch_size)
    ).mappings()
    return [dict(row) for row in result]

def delete_transaction_inferences_batch(
    session: Session,
    transaction_inferences: list[dict]
):
    session.execute(
        delete(TransactionInferences)
        .where(
            TransactionInferences.id.in_({
                item[TransactionInferences.id.key]
                for item in transaction_inferences
            })
        )
    )