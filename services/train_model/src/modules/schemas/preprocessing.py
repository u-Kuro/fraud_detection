from numpy import ndarray
from pydantic import BaseModel, ConfigDict
from sklearn.model_selection import StratifiedKFold

class PreprocessOutputs(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    X_train: ndarray
    X_test: ndarray
    y_train: ndarray
    y_test: ndarray
    original_y_train_positive_scale: float
    cross_validation: StratifiedKFold