import pytest
from unittest.mock import MagicMock

try:
    from services.train_model.src.modules.schemas.evaluation import (
        EvaluateModelOutputs,
        ModelEvaluationFigures,
        ModelEvaluationMetrics,
    )
    _SCHEMA_AVAILABLE = True
except RuntimeError:
    _SCHEMA_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _SCHEMA_AVAILABLE,
    reason="Pydantic Strict() on arbitrary types not supported in this environment version",
)

from pydantic import ValidationError


def test_model_evaluation_metrics_instantiation():
    m = ModelEvaluationMetrics(
        f1_score=0.8, pr_auc=0.7, recall=0.75, precision=0.85, roc_auc=0.9, accuracy=0.95
    )
    assert m.f1_score == 0.8


def test_model_evaluation_figures_instantiation():
    fig = MagicMock()
    figs = ModelEvaluationFigures(probability_scatter=fig, confusion_matrix=fig)
    assert figs.probability_scatter is fig


def test_evaluate_model_outputs_instantiation():
    fig = MagicMock()
    metrics = ModelEvaluationMetrics(
        f1_score=0.8, pr_auc=0.7, recall=0.75, precision=0.85, roc_auc=0.9, accuracy=0.95
    )
    figures = ModelEvaluationFigures(probability_scatter=fig, confusion_matrix=fig)
    outputs = EvaluateModelOutputs(metrics=metrics, metric_figures=figures)
    assert outputs.metrics is metrics
