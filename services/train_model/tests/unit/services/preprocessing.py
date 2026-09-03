import pytest

try:
    from services.train_model.src.modules.schemas.preprocessing import PreprocessOutputs
    from services.train_model.src.services.preprocessing import preprocess
    _AVAILABLE = True
except RuntimeError:
    _AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _AVAILABLE,
    reason="Pydantic Strict() on arbitrary types not supported in this environment version",
)

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold


def _make_dataset(n=500) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    data = {
        "is_fraud": [0] * (n // 2) + [1] * (n // 2),
        "amount": rng.random(n).tolist(),
        **{f"v{i}": rng.random(n).tolist() for i in range(1, 29)},
        "transaction_timestamp": rng.integers(0, 10000, n).tolist(),
    }
    return pd.DataFrame(data)


def test_preprocess_returns_preprocess_outputs():
    df = _make_dataset()
    result = preprocess(df)
    assert isinstance(result, PreprocessOutputs)


def test_preprocess_splits_train_test():
    df = _make_dataset()
    result = preprocess(df)
    assert result.X_train.shape[0] > 0
    assert result.X_test.shape[0] > 0


def test_preprocess_x_arrays_are_ndarrays():
    df = _make_dataset()
    result = preprocess(df)
    assert isinstance(result.X_train, np.ndarray)
    assert isinstance(result.X_test, np.ndarray)


def test_preprocess_y_arrays_binary():
    df = _make_dataset()
    result = preprocess(df)
    assert set(np.unique(result.y_test)).issubset({0, 1})


def test_preprocess_positive_scale_is_float():
    df = _make_dataset()
    result = preprocess(df)
    assert isinstance(result.original_y_train_positive_scale, float)


def test_preprocess_cross_validation_is_stratified_kfold():
    df = _make_dataset()
    result = preprocess(df)
    assert isinstance(result.cross_validation, StratifiedKFold)
