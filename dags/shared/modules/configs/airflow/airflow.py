from enum import Enum
from functools import cached_property

from pydantic import BaseModel, ConfigDict

class AirflowConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    OWNER: str = "mle"
    BASE_ENVIRONMENT_PREFIX: str = "AIRFLOW_VAR_"
    MLE_ENVIRONMENT_PREFIX: str = "MLE"

    @cached_property
    def ENVIRONMENT_PREFIX(self) -> str:
        return f"{self.BASE_ENVIRONMENT_PREFIX}{self.MLE_ENVIRONMENT_PREFIX}_"

airflow_config = AirflowConfig()

class DagIDs(str, Enum):
    CHALLENGER_MODEL_ROTATION = "CHALLENGER_MODEL_ROTATION"
    MODEL_LIFECYCLE_MONITOR = "MODEL_LIFECYCLE_MONITOR"
    TRAINING_APPROVAL_DISPATCH = "TRAINING_APPROVAL_DISPATCH"

class DriftMonitorKeys(str, Enum):
    DRIFT_DETECTED_KEY = "DRIFT_DETECTED"
    DRIFT_SUMMARY_KEY = "DRIFT_SUMMARY"