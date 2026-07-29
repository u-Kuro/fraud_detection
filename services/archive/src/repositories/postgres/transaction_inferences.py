from sqlalchemy import Connection, text

from services.archive.src.modules.configs.archive import ArchiveConfig
from services.archive.src.modules.environment.archive import archive_environment
from services.shared.modules.schemas.postgres.postgres import PostgresTableKeys
from services.shared.modules.schemas.postgres.transaction_inferences import TransactionInferencesColumnKeys


def get_transaction_inferences_batch(connection: Connection) -> list[dict]:
    transaction_inferences = connection.execute(text(f"""
        SELECT * FROM {PostgresTableKeys.transaction_inferences}
        WHERE {TransactionInferencesColumnKeys.transaction_timestamp} <= :cutoff
        ORDER BY
            {TransactionInferencesColumnKeys.transaction_timestamp},
            {TransactionInferencesColumnKeys.id}
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
    connection.execute(text(f"""
        DELETE FROM {PostgresTableKeys.transaction_inferences}
        WHERE {TransactionInferencesColumnKeys.id} = ANY(:{TransactionInferencesColumnKeys.id}::uuid[])
    """), {
        TransactionInferencesColumnKeys.id: [
            str(item["id"])
            for item in transaction_inferences
        ]
    })