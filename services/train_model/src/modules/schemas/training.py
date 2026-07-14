from typing import Any

from pydantic import BaseModel, ConfigDict

class TrainModelOutputs(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    model: object
    hyperparameters: dict[str, Any]