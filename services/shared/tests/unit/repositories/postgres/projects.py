from unittest.mock import MagicMock
from uuid import uuid4

from services.shared.src.repositories.postgres.projects import get_project_id

def test_get_project_id_returns_uuid(mocker):
    expected_id = uuid4()
    mock_session_ctx = MagicMock()
    mock_result = MagicMock()
    mock_result.one.return_value.t = (expected_id,)
    mock_session_ctx.__enter__ = MagicMock(return_value=MagicMock(
        execute=MagicMock(return_value=mock_result)
    ))
    mock_session_ctx.__exit__ = MagicMock(return_value=False)
    mock_session = MagicMock()
    mock_session.begin.return_value = mock_session_ctx

    mocker.patch(
        "services.shared.repositories.postgres.projects.sql_session",
        mock_session,
    )

    result = get_project_id("fraud_detection")
    assert result == expected_id

def test_get_project_id_queries_with_project_name(mocker):
    expected_id = uuid4()
    mock_session = MagicMock()
    mock_execute = MagicMock()
    mock_execute.one.return_value.t = (expected_id,)
    mock_inner_session = MagicMock(execute=MagicMock(return_value=mock_execute))
    mock_ctx = MagicMock(__enter__=MagicMock(return_value=mock_inner_session), __exit__=MagicMock(return_value=False))
    mock_session.begin.return_value = mock_ctx

    mocker.patch(
        "services.shared.repositories.postgres.projects.sql_session",
        mock_session,
    )

    get_project_id("test_project")
    assert mock_session.begin.called