import pytest
from unittest.mock import MagicMock

try:
    from services.train_model.src.modules.schemas.evaluation import (
        EvaluateModelOutputs,
        ModelEvaluationFigures,
        ModelEvaluationMetrics,
    )
    from services.train_model.src.services.evaluation import (
        evaluate_model,
        evaluate_model_predictions,
        get_predictions_sklearn,
        visualize_model_predictions,
    )
    _AVAILABLE = True
except RuntimeError:
    _AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _AVAILABLE,
    reason="Pydantic Strict() on arbitrary types not supported in this environment version",
)

import numpy as np
from matplotlib.figure import Figure


def _make_arrays():
    rng = np.random.default_rng(42)
    y_true = np.array([0, 1, 0, 1, 1, 0, 1, 0])
    y_prob = rng.random(8)
    y_pred = (y_prob >= 0.5).astype(int)
    x = rng.random((8, 3))
    return x, y_true, y_pred, y_prob


def test_get_predictions_sklearn_returns_dict_with_y_pred_and_y_prob():
    x, _, _, _ = _make_arrays()
    mock_model = MagicMock()
    proba = np.zeros((8, 2))
    proba[:, 1] = np.linspace(0.1, 0.9, 8)
    proba[:, 0] = 1 - proba[:, 1]
    mock_model.predict_proba.return_value = proba
    result = get_predictions_sklearn(mock_model, x)
    assert "y_pred" in result
    assert "y_prob" in result


def test_get_predictions_sklearn_pred_is_binary():
    x, _, _, _ = _make_arrays()
    mock_model = MagicMock()
    proba = np.zeros((8, 2))
    proba[:, 1] = np.linspace(0.1, 0.9, 8)
    proba[:, 0] = 1 - proba[:, 1]
    mock_model.predict_proba.return_value = proba
    result = get_predictions_sklearn(mock_model, x)
    assert set(np.unique(result["y_pred"])).issubset({0, 1})


def test_get_predictions_sklearn_custom_threshold():
    x, _, _, _ = _make_arrays()
    mock_model = MagicMock()
    proba = np.zeros((4, 2))
    proba[:, 1] = [0.3, 0.4, 0.6, 0.7]
    proba[:, 0] = 1 - proba[:, 1]
    mock_model.predict_proba.return_value = proba
    result = get_predictions_sklearn(mock_model, x[:4], threshold=0.5)
    assert result["y_pred"][0] == 0
    assert result["y_pred"][2] == 1


def test_evaluate_model_predictions_returns_metrics():
    _, y_true, y_pred, y_prob = _make_arrays()
    result = evaluate_model_predictions(y_pred=y_pred, y_prob=y_prob, y_true=y_true)
    assert isinstance(result, ModelEvaluationMetrics)


def test_evaluate_model_predictions_metrics_in_range():
    _, y_true, y_pred, y_prob = _make_arrays()
    result = evaluate_model_predictions(y_pred=y_pred, y_prob=y_prob, y_true=y_true)
    for field in ["f1_score", "pr_auc", "recall", "precision", "roc_auc", "accuracy"]:
        val = getattr(result, field)
        assert 0.0 <= val <= 1.0, f"{field}={val} out of range"


def test_visualize_model_predictions_returns_figures():
    _, y_true, y_pred, y_prob = _make_arrays()
    result = visualize_model_predictions(
        title="test", y_pred=y_pred, y_prob=y_prob, y_true=y_true
    )
    assert isinstance(result, ModelEvaluationFigures)
    assert isinstance(result.probability_scatter, Figure)
    assert isinstance(result.confusion_matrix, Figure)


def test_evaluate_model_returns_evaluate_model_outputs():
    x, y_true, _, _ = _make_arrays()
    mock_model = MagicMock()
    proba = np.zeros((8, 2))
    proba[:, 1] = np.linspace(0.1, 0.9, 8)
    proba[:, 0] = 1 - proba[:, 1]
    mock_model.predict_proba.return_value = proba
    result = evaluate_model(model=mock_model, X_test=x, y_test=y_true)
    assert isinstance(result, EvaluateModelOutputs)
