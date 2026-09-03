from unittest.mock import MagicMock
from uuid import uuid4

from dags.shared.repositories.postgres.projects import get_project_id

def test_get_project_id_returns_uuid(mocker):
    expected = uuid4()
    mock_session = MagicMock()
    mock_result = MagicMock()
    mock_result.one.return_value.t = (expected,)
    mock_inner = MagicMock()
    mock_inner.execute.return_value = mock_result
    mock_ctx = MagicMock()
    mock_ctx.__enter__ = MagicMock(return_value=mock_inner)
    mock_ctx.__exit__ = MagicMock(return_value=False)
    mock_session.begin.return_value = mock_ctx
    mocker.patch(
        "dags.shared.repositories.postgres.projects.sql_session",
        mock_session,
    )
    result = get_project_id("fraud_detection")
    assert result == expected

def test_get_project_id_passes_project_name(mocker):
    expected = uuid4()
    mock_session = MagicMock()
    mock_result = MagicMock()
    mock_result.one.return_value.t = (expected,)
    mock_inner = MagicMock()
    mock_inner.execute.return_value = mock_result
    mock_ctx = MagicMock()
    mock_ctx.__enter__ = MagicMock(return_value=mock_inner)
    mock_ctx.__exit__ = MagicMock(return_value=False)
    mock_session.begin.return_value = mock_ctx
    mocker.patch(
        "dags.shared.repositories.postgres.projects.sql_session",
        mock_session,
    )
    get_project_id("my_project")
    mock_session.begin.assert_called_once()
