import pytest

try:
    from services.train_model.src.modules.schemas.postgres.transaction_inferences import (
        TransactionInferencesDatasetNow,
    )
    _SCHEMA_AVAILABLE = True
except RuntimeError:
    _SCHEMA_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _SCHEMA_AVAILABLE,
    reason="Pydantic Strict() on arbitrary types not supported in this environment version",
)

from datetime import datetime, timezone
import pandas as pd


def test_transaction_inferences_dataset_now_instantiation():
    df = pd.DataFrame({"col": [1, 2]})
    now = datetime.now(timezone.utc)
    obj = TransactionInferencesDatasetNow(dataset=df, retrieved_datetime=now)
    assert obj.retrieved_datetime == now


def test_transaction_inferences_dataset_now_stores_dataframe():
    df = pd.DataFrame({"col": [1, 2]})
    now = datetime.now(timezone.utc)
    obj = TransactionInferencesDatasetNow(dataset=df, retrieved_datetime=now)
    assert isinstance(obj.dataset, pd.DataFrame)
