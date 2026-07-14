from typing import Any

from matplotlib.figure import Figure
from pydantic import BaseModel, ConfigDict

class EvaluateModelOutputs(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    metrics: dict[str, Any]
    metric_figures: dict[str, Figure]