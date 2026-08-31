from typing import Annotated

from numpy import ndarray
from pydantic import BaseModel, ConfigDict, StrictFloat, Strict
from sklearn.model_selection import StratifiedKFold

class PreprocessOutputs(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    X_train: Annotated[ndarray, Strict()]
    X_test: Annotated[ndarray, Strict()]
    y_train: Annotated[ndarray, Strict()]
    y_test: Annotated[ndarray, Strict()]
    original_y_train_positive_scale: StrictFloat
    cross_validation: Annotated[StratifiedKFold, Strict()]