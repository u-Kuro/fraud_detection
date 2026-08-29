from matplotlib.figure import Figure
from pydantic import BaseModel, ConfigDict


class ModelEvaluationMetrics(BaseModel):
    f1_score: float
    pr_auc: float
    recall: float
    precision: float
    roc_auc: float
    accuracy: float

class ModelEvaluationFigures(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    probability_scatter: Figure
    confusion_matrix: Figure

class EvaluateModelOutputs(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    metrics: ModelEvaluationMetrics
    metric_figures: ModelEvaluationFigures