from typing import Annotated

from matplotlib.figure import Figure
from pydantic import BaseModel, ConfigDict, Strict, StrictFloat

class ModelEvaluationMetrics(BaseModel):
    f1_score: StrictFloat
    pr_auc: StrictFloat
    recall: StrictFloat
    precision: StrictFloat
    roc_auc: StrictFloat
    accuracy: StrictFloat

class ModelEvaluationFigures(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    probability_scatter: Annotated[Figure, Strict()]
    confusion_matrix: Annotated[Figure, Strict()]

class EvaluateModelOutputs(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    metrics: Annotated[ModelEvaluationMetrics, Strict()]
    metric_figures: Annotated[ModelEvaluationFigures, Strict()]