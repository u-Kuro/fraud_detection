from collections import defaultdict
from datetime import date

from services.archive.src.repositories.s3.archive import upload_transaction_inference_batch

def make_batch(dates_and_rows: dict) -> tuple[defaultdict, defaultdict]:
    by_date: defaultdict[date, list[dict]] = defaultdict(list)
    batch_by_date: defaultdict[date, int] = defaultdict(int)
    for d, rows in dates_and_rows.items():
        by_date[d].extend(rows)
        batch_by_date[d] = 1
    return by_date, batch_by_date

def patch_pyarrow_and_parquet(mocker):
    # pyarrow.lib.Table is a C extension type — its class methods are immutable
    # and cannot be patched directly. Patch the module-level name instead.
    mock_pyarrow = mocker.patch("services.archive.src.repositories.s3.archive.pyarrow")
    mock_parquet = mocker.patch("services.archive.src.repositories.s3.archive.parquet")
    return mock_pyarrow, mock_parquet

def test_upload_calls_s3_upload_fileobj(mocker):
    mock_client = mocker.patch("services.archive.src.repositories.s3.archive.s3_client")
    patch_pyarrow_and_parquet(mocker)

    d = date(2025, 1, 1)
    by_date: defaultdict[date, list[dict]] = defaultdict(list)
    by_date[d].append({"id": 1})
    batch_by_date: defaultdict[date, int] = defaultdict(int)
    batch_by_date[d] = 0

    upload_transaction_inference_batch(by_date, batch_by_date)

    mock_client.upload_fileobj.assert_called_once()

def test_upload_uses_date_partition_in_key(mocker):
    mock_client = mocker.patch("services.archive.src.repositories.s3.archive.s3_client")
    patch_pyarrow_and_parquet(mocker)

    d = date(2025, 3, 15)
    by_date: defaultdict[date, list[dict]] = defaultdict(list)
    by_date[d].append({"id": 1})
    batch_by_date: defaultdict[date, int] = defaultdict(int)
    batch_by_date[d] = 0

    upload_transaction_inference_batch(by_date, batch_by_date)

    call_kwargs = mock_client.upload_fileobj.call_args[1]
    assert "year=2025" in call_kwargs["Key"]
    assert "month=03" in call_kwargs["Key"]
    assert "day=15" in call_kwargs["Key"]

def test_upload_empty_by_date_does_nothing(mocker):
    mock_client = mocker.patch("services.archive.src.repositories.s3.archive.s3_client")
    by_date: defaultdict[date, list[dict]] = defaultdict(list)
    batch_by_date: defaultdict[date, int] = defaultdict(int)

    upload_transaction_inference_batch(by_date, batch_by_date)

    mock_client.upload_fileobj.assert_not_called()
