import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_sql_session(mocker):
    session_ctx = MagicMock()
    session_ctx.__enter__ = MagicMock(return_value=MagicMock())
    session_ctx.__exit__ = MagicMock(return_value=False)
    mock_session = MagicMock()
    mock_session.begin.return_value = session_ctx
    return mock_session

@pytest.fixture
def mock_s3_client(mocker):
    return MagicMock()

@pytest.fixture
def mock_mlflow_client(mocker):
    return MagicMock()

@pytest.fixture
def mock_mlflow_module(mocker):
    return MagicMock()
