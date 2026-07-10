from functools import cached_property

from pydantic import BaseModel, ConfigDict

class AirflowConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    OWNER: str = "mle"
    BASE_ENVIRONMENT_PREFIX = "AIRFLOW_VAR_"
    MLE_ENVIRONMENT_PREFIX: str = "MLE"

    @cached_property
    def ENVIRONMENT_PREFIX(self) -> str:
        return f"{self.BASE_ENVIRONMENT_PREFIX}{self.MLE_ENVIRONMENT_PREFIX}_"

airflow_config = AirflowConfig()