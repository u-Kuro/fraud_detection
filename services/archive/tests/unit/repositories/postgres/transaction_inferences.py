from datetime import datetime, timezone
from unittest.mock import MagicMock

from services.archive.src.repositories.postgres.transaction_inferences import delete_transaction_inferences_batch, get_transaction_inferences_batch

def make_session(rows=None):
    mock_result = MagicMock()
    mock_result.mappings.return_value = rows or []
    mock_session = MagicMock()
    mock_session.execute.return_value = mock_result
    return mock_session

def test_get_transaction_inferences_batch_returns_list(mocker):
    cutoff = datetime(2025, 1, 1, tzinfo=timezone.utc)
    mocker.patch(
        "services.archive.src.repositories.postgres.transaction_inferences.archive_environment"
    ).TRANSACTION_INFERENCES_ISO_DATETIME_CUTOFF = cutoff

    mock_session = make_session([{"id": 1, "transaction_timestamp": cutoff}])
    result = get_transaction_inferences_batch(mock_session)
    assert isinstance(result, list)

def test_get_transaction_inferences_batch_maps_rows_to_dicts(mocker):
    cutoff = datetime(2025, 1, 1, tzinfo=timezone.utc)
    mocker.patch(
        "services.archive.src.repositories.postgres.transaction_inferences.archive_environment"
    ).TRANSACTION_INFERENCES_ISO_DATETIME_CUTOFF = cutoff

    row = {"id": 42, "amount": 1.5}
    mock_result = MagicMock()
    mock_result.mappings.return_value = [row]
    mock_session = MagicMock()
    mock_session.execute.return_value = mock_result

    result = get_transaction_inferences_batch(mock_session)
    assert result[0]["id"] == 42

def test_get_transaction_inferences_batch_empty_when_no_rows(mocker):
    cutoff = datetime(2025, 1, 1, tzinfo=timezone.utc)
    mocker.patch(
        "services.archive.src.repositories.postgres.transaction_inferences.archive_environment"
    ).TRANSACTION_INFERENCES_ISO_DATETIME_CUTOFF = cutoff

    mock_session = make_session([])
    result = get_transaction_inferences_batch(mock_session)
    assert result == []

def test_delete_transaction_inferences_batch_executes_delete(mocker):
    mock_session = MagicMock()
    batch = [{"id": 1}, {"id": 2}]
    delete_transaction_inferences_batch(mock_session, batch)
    mock_session.execute.assert_called_once()

def test_delete_transaction_inferences_batch_empty_list(mocker):
    mock_session = MagicMock()
    delete_transaction_inferences_batch(mock_session, [])
    mock_session.execute.assert_called_once()
