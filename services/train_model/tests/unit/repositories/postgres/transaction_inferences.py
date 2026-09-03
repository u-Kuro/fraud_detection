import pytest
import pandas as pd
from unittest.mock import MagicMock
from uuid import uuid4

# TransactionInferencesDatasetNow uses Strict() on arbitrary types — guard
# against the pydantic 2.13.5 regression that affects this environment.
try:
    from services.train_model.src.repositories.postgres.transaction_inferences import (
        get_timed_latest_unused_dataset,
    )
    _AVAILABLE = True
except RuntimeError:
    _AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _AVAILABLE,
    reason="Pydantic Strict() on arbitrary types not supported in this environment version",
)


def _make_session_mock(df: pd.DataFrame, project_id=None):
    mock_conn = MagicMock()
    mock_inner = MagicMock()
    mock_inner.connection.return_value = mock_conn
    mock_ctx = MagicMock()
    mock_ctx.__enter__ = MagicMock(return_value=mock_inner)
    mock_ctx.__exit__ = MagicMock(return_value=False)
    mock_sm = MagicMock()
    mock_sm.begin.return_value = mock_ctx
    return mock_sm


def test_get_timed_latest_unused_dataset_raises_type_error_non_dataframe(mocker):
    mock_sm = _make_session_mock(None)
    mocker.patch(
        "services.train_model.src.repositories.postgres.transaction_inferences.sql_session",
        mock_sm,
    )
    mocker.patch(
        "services.train_model.src.repositories.postgres.transaction_inferences.PostgresConfig"
    ).project_id.return_value = uuid4()
    mocker.patch(
        "services.train_model.src.repositories.postgres.transaction_inferences.pandas.read_sql",
        return_value="not a dataframe",
    )
    with pytest.raises(TypeError):
        get_timed_latest_unused_dataset()


def test_get_timed_latest_unused_dataset_raises_value_error_small_dataset(mocker):
    small_df = pd.DataFrame({"col": range(10)})
    mock_sm = _make_session_mock(small_df)
    mocker.patch(
        "services.train_model.src.repositories.postgres.transaction_inferences.sql_session",
        mock_sm,
    )
    mocker.patch(
        "services.train_model.src.repositories.postgres.transaction_inferences.PostgresConfig"
    ).project_id.return_value = uuid4()
    mocker.patch(
        "services.train_model.src.repositories.postgres.transaction_inferences.pandas.read_sql",
        return_value=small_df,
    )
    with pytest.raises(ValueError, match="too small"):
        get_timed_latest_unused_dataset()
