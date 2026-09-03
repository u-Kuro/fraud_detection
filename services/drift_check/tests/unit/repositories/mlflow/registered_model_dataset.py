from datetime import datetime
from unittest.mock import MagicMock

import pandas as pd

def test_load_reference_dataset_calls_download_artifacts(mocker):
    mock_mlflow_module = mocker.patch("services.drift_check.src.repositories.mlflow.registered_model_dataset.mlflow_module")
    mock_table = MagicMock()
    mock_df = pd.DataFrame({"transaction_timestamp": [1.0, 2.0, 3.0]})
    mock_table.to_pandas.return_value = mock_df

    mocker.patch(
        "services.drift_check.src.repositories.mlflow.registered_model_dataset.parquet.read_table",
        return_value=mock_table,
    )

    from services.drift_check.src.repositories.mlflow.registered_model_dataset import load_reference_dataset
    df, cutoff = load_reference_dataset()

    mock_mlflow_module.artifacts.download_artifacts.assert_called_once()

def test_load_reference_dataset_returns_dataframe_and_datetime(mocker):
    mock_mlflow_module = mocker.patch("services.drift_check.src.repositories.mlflow.registered_model_dataset.mlflow_module")
    mock_table = MagicMock()
    mock_df = pd.DataFrame({"transaction_timestamp": [1609459200.0]})
    mock_table.to_pandas.return_value = mock_df
    mocker.patch(
        "services.drift_check.src.repositories.mlflow.registered_model_dataset.parquet.read_table",
        return_value=mock_table,
    )

    from services.drift_check.src.repositories.mlflow.registered_model_dataset import load_reference_dataset
    df, cutoff = load_reference_dataset()

    assert isinstance(df, pd.DataFrame)
    assert isinstance(cutoff, datetime)
