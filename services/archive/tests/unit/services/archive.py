from datetime import datetime

from pytest_mock import MockerFixture

from services.shared.src.modules.schemas.postgres.transaction_inferences import TransactionInferences

def test_archive_transaction_inferences(mocker: MockerFixture):
    mocker.patch(
        target="services.archive.src.repositories.postgres.transaction_inferences.get_transaction_inferences_batch",
        return_value=[{
            TransactionInferences.transaction_timestamp.key: datetime.now()
        }]
    )
    mocker.patch("services.archive.src.repositories.s3.archive.upload_transaction_inference_batch")
    mocker.patch("services.archive.src.repositories.postgres.transaction_inferences.delete_transaction_inferences_batch")

    tested_function = mocker.patch("services.archive.src.services.archive.archive_transaction_inferences")

    from services.archive.src.services.archive import archive_transaction_inferences
    archive_transaction_inferences()

    tested_function.assert_called_once()
