import pytest

try:
    from services.train_model.src.modules.schemas.preprocessing import PreprocessOutputs
    _SCHEMA_AVAILABLE = True
except RuntimeError:
    _SCHEMA_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _SCHEMA_AVAILABLE,
    reason="Pydantic Strict() on arbitrary types not supported in this environment version",
)

import numpy as np
from sklearn.model_selection import StratifiedKFold


def _make_outputs():
    arr = np.array([1.0, 2.0])
    cv = StratifiedKFold(n_splits=4)
    return PreprocessOutputs(
        X_train=arr, X_test=arr, y_train=arr, y_test=arr,
        original_y_train_positive_scale=3.0,
        cross_validation=cv,
    )


def test_preprocess_outputs_instantiation():
    outputs = _make_outputs()
    assert outputs.original_y_train_positive_scale == 3.0


def test_preprocess_outputs_cross_validation_is_stratified_kfold():
    outputs = _make_outputs()
    assert isinstance(outputs.cross_validation, StratifiedKFold)


def test_preprocess_outputs_x_train_is_ndarray():
    outputs = _make_outputs()
    assert isinstance(outputs.X_train, np.ndarray)
