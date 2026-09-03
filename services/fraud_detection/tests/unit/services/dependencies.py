import asyncio
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from services.fraud_detection.src.services.dependencies import check_postgres, get_executor, get_model

def test_check_postgres_succeeds_when_db_is_reachable(mocker):
    mock_inner = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.__enter__ = MagicMock(return_value=mock_inner)
    mock_ctx.__exit__ = MagicMock(return_value=False)
    mock_sm = MagicMock()
    mock_sm.begin.return_value = mock_ctx
    mocker.patch(
        "services.fraud_detection.src.services.dependencies.sql_session",
        mock_sm,
    )
    check_postgres()

def test_check_postgres_raises_503_on_error(mocker):
    mock_sm = MagicMock()
    mock_sm.begin.side_effect = Exception("connection refused")
    mocker.patch(
        "services.fraud_detection.src.services.dependencies.sql_session",
        mock_sm,
    )
    with pytest.raises(HTTPException) as exc_info:
        check_postgres()
    assert exc_info.value.status_code == 503

def test_get_executor_returns_executor_when_ready():
    mock_request = MagicMock()
    mock_executor = MagicMock()
    mock_request.app.state.executor = mock_executor
    result = asyncio.run(get_executor(mock_request))
    assert result is mock_executor

def test_get_executor_raises_503_when_none():
    mock_request = MagicMock()
    mock_request.app.state.executor = None
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(get_executor(mock_request))
    assert exc_info.value.status_code == 503

def test_get_model_returns_model_when_ready():
    mock_request = MagicMock()
    mock_model = MagicMock()
    mock_request.app.state.model = mock_model
    result = asyncio.run(get_model(mock_request))
    assert result is mock_model

def test_get_model_raises_503_when_none():
    mock_request = MagicMock()
    mock_request.app.state.model = None
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(get_model(mock_request))
    assert exc_info.value.status_code == 503