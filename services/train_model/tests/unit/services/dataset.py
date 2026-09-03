import pandas as pd
import pytest

from services.train_model.src.modules.schemas.postgres.model_deployment_workflows import (
    ModelDeploymentWorkflowDatasetTimestamps,
)
from services.train_model.src.services.dataset import get_dataset_min_and_max_timestamps


def test_get_dataset_min_and_max_returns_correct_type():
    df = pd.DataFrame({"transaction_timestamp": pd.to_datetime(["2025-01-01", "2025-06-01"])})
    result = get_dataset_min_and_max_timestamps(df, "transaction_timestamp")
    assert isinstance(result, ModelDeploymentWorkflowDatasetTimestamps)


def test_get_dataset_min_and_max_min_is_earlier():
    df = pd.DataFrame({
        "transaction_timestamp": pd.to_datetime(["2025-01-01", "2025-06-01", "2025-03-15"])
    })
    result = get_dataset_min_and_max_timestamps(df, "transaction_timestamp")
    assert "2025-01-01" in result.model_dataset_min_iso_datetime


def test_get_dataset_min_and_max_max_is_later():
    df = pd.DataFrame({
        "transaction_timestamp": pd.to_datetime(["2025-01-01", "2025-06-01", "2025-03-15"])
    })
    result = get_dataset_min_and_max_timestamps(df, "transaction_timestamp")
    assert "2025-06-01" in result.model_dataset_max_iso_datetime


def test_get_dataset_min_and_max_single_row():
    df = pd.DataFrame({"transaction_timestamp": pd.to_datetime(["2025-03-01"])})
    result = get_dataset_min_and_max_timestamps(df, "transaction_timestamp")
    assert "2025-03-01" in result.model_dataset_min_iso_datetime
    assert result.model_dataset_min_iso_datetime == result.model_dataset_max_iso_datetime
