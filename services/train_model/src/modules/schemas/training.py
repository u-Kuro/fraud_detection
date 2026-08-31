from typing import Any, Annotated

from pydantic import BaseModel, ConfigDict, StrictStr, Strict


class TrainModelOutputs(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    model: Annotated[object, Strict()]
    hyperparameters: Annotated[dict[StrictStr, Any], Strict()]