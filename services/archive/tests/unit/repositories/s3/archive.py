from collections import defaultdict
from datetime import date

from pytest_mock import MockerFixture

def test_upload_transaction_inference_batch(mocker: MockerFixture):
    tested_function = mocker.patch("services.archive.src.services.archive.archive_transaction_inferences")

    from services.archive.src.repositories.s3.archive import upload_transaction_inference_batch
    today = date.today()
    upload_transaction_inference_batch(
        transaction_inferences_by_date=defaultdict(list[dict], {
            today: [{"key": "value"}],
        }),
        batch_by_date=defaultdict(int, {
            today: 1
        })
    )

    tested_function.assert_called_once()