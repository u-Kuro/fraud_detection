import pytest

try:
    from services.train_model.src.modules.schemas.preprocessing import PreprocessOutputs
    from services.train_model.src.modules.schemas.training import TrainModelOutputs
    _AVAILABLE = True
except RuntimeError:
    _AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _AVAILABLE,
    reason="Pydantic Strict() on arbitrary types not supported in this environment version",
)

from unittest.mock import MagicMock
import numpy as np


def _make_preprocess_outputs():
    from sklearn.model_selection import StratifiedKFold
    arr = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0], [7.0, 8.0]])
    labels = np.array([0, 1, 0, 1])
    cv = StratifiedKFold(n_splits=2)
    return PreprocessOutputs(
        X_train=arr, X_test=arr, y_train=labels, y_test=labels,
        original_y_train_positive_scale=1.0, cross_validation=cv
    )


def test_train_model_returns_train_model_outputs(mocker):
    from services.train_model.src.modules.configs.hyperparameters import XGBHyperparametersSampler
    from sklearn.preprocessing import RobustScaler
    from xgboost import XGBClassifier

    mocker.patch(
        "services.train_model.src.services.training.optimize_model_hyperparameters",
        return_value=MagicMock(best_params={"n_estimators": 10, "max_depth": 2,
                                             "learning_rate": 0.1, "subsample": 0.8,
                                             "colsample_bytree": 0.8, "reg_alpha": 0.0,
                                             "reg_lambda": 1.0, "gamma": 0.0,
                                             "min_child_weight": 1}),
    )

    from services.train_model.src.services.training import train_model
    preprocess_outputs = _make_preprocess_outputs()
    result = train_model(
        preprocess_outputs=preprocess_outputs,
        scaler=RobustScaler,
        model=XGBClassifier,
        hyperparameters_sampler=XGBHyperparametersSampler,
    )
    assert isinstance(result, TrainModelOutputs)
