from airflow.sdk.types import TaskInstance
from pydantic import BaseModel, ConfigDict

class AirflowTaskContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    ti: TaskInstance

    @classmethod
    def from_context(cls, context: dict) -> "AirflowTaskContext":
        return cls(ti=context["ti"])

class AirflowDAGRunConfigurationsContext(BaseModel):
    conf: dict

    @classmethod
    def from_context(cls, context: dict) -> "AirflowDAGRunConfigurationsContext":
        return cls(conf=context["dag_run"].conf)