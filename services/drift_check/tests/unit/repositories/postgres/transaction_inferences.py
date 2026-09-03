from datetime import datetime, timezone
from unittest.mock import MagicMock

import pandas as pd
import pytest

from services.drift_check.src.repositories.postgres.transaction_inferences import load_current_dataset

def make_sql_session_mock(df: pd.DataFrame):
    mock_conn = MagicMock()
    mock_inner = MagicMock()
    mock_inner.connection.return_value = mock_conn

    mock_ctx = MagicMock()
    mock_ctx.__enter__ = MagicMock(return_value=mock_inner)
    mock_ctx.__exit__ = MagicMock(return_value=False)

    mock_sm = MagicMock()
    mock_sm.begin.return_value = mock_ctx
    return mock_sm


def test_load_current_dataset_raises_type_error_for_non_dataframe(mocker):
    cutoff = datetime(2025, 1, 1, tzinfo=timezone.utc)
    mock_sm = make_sql_session_mock(None)
    mocker.patch(
        "services.drift_check.src.repositories.postgres.transaction_inferences.sql_session",
        mock_sm,
    )
    mocker.patch(
        "services.drift_check.src.repositories.postgres.transaction_inferences.pandas.read_sql",
        return_value="not a dataframe",
    )
    with pytest.raises(TypeError):
        load_current_dataset(cutoff)


def test_load_current_dataset_raises_value_error_for_small_dataset(mocker):
    cutoff = datetime(2025, 1, 1, tzinfo=timezone.utc)
    small_df = pd.DataFrame({"col": range(10)})
    mock_sm = make_sql_session_mock(small_df)
    mocker.patch(
        "services.drift_check.src.repositories.postgres.transaction_inferences.sql_session",
        mock_sm,
    )
    mocker.patch(
        "services.drift_check.src.repositories.postgres.transaction_inferences.pandas.read_sql",
        return_value=small_df,
    )
    with pytest.raises(ValueError, match="too small"):
        load_current_dataset(cutoff)
