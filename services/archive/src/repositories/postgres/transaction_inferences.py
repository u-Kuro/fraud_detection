from sqlalchemy import Connection, text

from services.archive.src.modules.configs.archive import ArchiveConfig
from services.archive.src.modules.environment.archive import archive_environment

def get_transaction_inferences_batch(connection: Connection) -> list[dict]:
    transaction_inferences = connection.execute(text("""
        SELECT * FROM transaction_inferences
        WHERE transaction_timestamp <= :cutoff
        ORDER BY transaction_timestamp, id
        LIMIT :batch_size
    """), {
        "cutoff": archive_environment.TRANSACTION_INFERENCES_ARCHIVE_CUTOFF_ISO_DATETIME,
        "batch_size": ArchiveConfig.batch_size
    }).mappings().fetchall()

    return [
        dict(item)
        for item in transaction_inferences
    ]

def delete_transaction_inferences_batch(
    connection: Connection,
    transaction_inferences: list[dict]
):
    connection.execute(text("""
        DELETE FROM transaction_inferences
        WHERE id = ANY(:ids::uuid[])
    """), {
        "ids": [
            str(item["id"])
            for item in transaction_inferences
        ]
    })