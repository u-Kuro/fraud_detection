from datetime import datetime

import pytest
from pytest_mock import MockerFixture

from services.shared.src.modules.schemas.postgres.transaction_inferences import TransactionInferences

@pytest.fixture
def mocked_upload_transaction_inference_batch(mocker: MockerFixture):
    mocker.patch("services.archive.src.repositories.s3.archive.upload_transaction_inference_batch")
    mocker.patch("services.archive.src.repositories.postgres.transaction_inferences.delete_transaction_inferences_batch")
    mocker.patch(
        target="services.archive.src.repositories.postgres.transaction_inferences.get_transaction_inferences_batch",
        return_value=[{
            TransactionInferences.transaction_timestamp.key: datetime.now()
        }]
    )

    return mocker.patch("services.archive.src.services.archive.archive_transaction_inferences")

def test_archive_groups_rows_by_date(mocked_upload_transaction_inference_batch):
    mocked_upload_transaction_inference_batch.assert_called_once()
