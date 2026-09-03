from datetime import datetime, date, timezone
from unittest.mock import MagicMock

from services.archive.src.services.archive import archive_transaction_inferences

def make_session_ctx(rows: list[dict]):
    mock_session = MagicMock()
    mock_session.execute.side_effect = [
        MagicMock(mappings=MagicMock(return_value=rows)),
        MagicMock(),  # delete call
    ]

    mock_ctx = MagicMock()
    mock_ctx.__enter__ = MagicMock(return_value=mock_session)
    mock_ctx.__exit__ = MagicMock(return_value=False)
    return mock_ctx

def test_archive_transaction_inferences_calls_ensure_bucket(mocker):
    mock_ensure = mocker.patch("services.archive.src.services.archive.ensure_bucket")
    mock_get = mocker.patch(
        "services.archive.src.services.archive.get_transaction_inferences_batch",
        return_value=[],
    )
    mocker.patch("services.archive.src.services.archive.sql_session")

    archive_transaction_inferences()

    mock_ensure.assert_called_once()

def test_archive_transaction_inferences_stops_when_empty_batch(mocker):
    mocker.patch("services.archive.src.services.archive.ensure_bucket")
    mock_get = mocker.patch(
        "services.archive.src.services.archive.get_transaction_inferences_batch",
        return_value=[],
    )
    mock_upload = mocker.patch("services.archive.src.services.archive.upload_transaction_inference_batch")
    mock_session = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.__enter__ = MagicMock(return_value=mock_session)
    mock_ctx.__exit__ = MagicMock(return_value=False)
    mock_session_maker = MagicMock()
    mock_session_maker.begin.return_value = mock_ctx
    mocker.patch(
        "services.archive.src.services.archive.sql_session",
        mock_session_maker,
    )

    archive_transaction_inferences()

    mock_upload.assert_not_called()


def test_archive_transaction_inferences_uploads_and_deletes(mocker):
    mocker.patch("services.archive.src.services.archive.ensure_bucket")

    ts = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    rows = [{"transaction_timestamp": ts, "id": 1}]

    # First call returns rows, second call returns empty (stop)
    mock_get = mocker.patch(
        "services.archive.src.services.archive.get_transaction_inferences_batch",
        side_effect=[rows, []],
    )
    mock_upload = mocker.patch("services.archive.src.services.archive.upload_transaction_inference_batch")
    mock_delete = mocker.patch("services.archive.src.services.archive.delete_transaction_inferences_batch")

    mock_session = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.__enter__ = MagicMock(return_value=mock_session)
    mock_ctx.__exit__ = MagicMock(return_value=False)
    mock_sm = MagicMock()
    mock_sm.begin.return_value = mock_ctx
    mocker.patch("services.archive.src.services.archive.sql_session", mock_sm)

    archive_transaction_inferences()

    mock_upload.assert_called_once()
    mock_delete.assert_called_once()


def test_archive_groups_rows_by_date(mocker):
    mocker.patch("services.archive.src.services.archive.ensure_bucket")

    ts1 = datetime(2025, 1, 1, tzinfo=timezone.utc)
    ts2 = datetime(2025, 1, 2, tzinfo=timezone.utc)
    rows = [
        {"transaction_timestamp": ts1, "id": 1},
        {"transaction_timestamp": ts2, "id": 2},
        {"transaction_timestamp": ts1, "id": 3},
    ]

    mocker.patch(
        "services.archive.src.services.archive.get_transaction_inferences_batch",
        side_effect=[rows, []],
    )
    mock_upload = mocker.patch("services.archive.src.services.archive.upload_transaction_inference_batch")
    mocker.patch("services.archive.src.services.archive.delete_transaction_inferences_batch")

    mock_session = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.__enter__ = MagicMock(return_value=mock_session)
    mock_ctx.__exit__ = MagicMock(return_value=False)
    mock_sm = MagicMock()
    mock_sm.begin.return_value = mock_ctx
    mocker.patch("services.archive.src.services.archive.sql_session", mock_sm)

    archive_transaction_inferences()

    by_date_arg = mock_upload.call_args[0][0]
    assert date(2025, 1, 1) in by_date_arg
    assert date(2025, 1, 2) in by_date_arg
    assert len(by_date_arg[date(2025, 1, 1)]) == 2
