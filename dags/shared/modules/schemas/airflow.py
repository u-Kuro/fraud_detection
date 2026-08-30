from typing import Any

from airflow.sdk import Context
# noinspection protected-member
from airflow.sdk.types import RuntimeTaskInstanceProtocol, DagRunProtocol
from pydantic import BaseModel

class TaskDAGRun:
    def __init__(self, dag_run: DagRunProtocol):
        self.dag_run = dag_run

    @property
    def configurations(self) -> dict[str, Any]:
        conf = self.dag_run.conf
        if conf is None:
            raise TypeError(f"Expected a dict, got None.")
        else:
            return conf

class TaskContext:
    def __init__(self, context: Context):
        self.context = context
        self.exception = context["exception"]

    def resolve_task_id(self, task_id: str) -> str:
        current_task_id = self.task_instance.task_id
        if "." in current_task_id:
            task_group_path = current_task_id.rsplit(".", 1)[0]
            return f"{task_group_path}.{task_id}"
        else:
            return task_id

    def xcom_pull[T: BaseModel](self, pydantic_model: type[T]) -> T:
        return pydantic_model.model_validate(self)

    @property
    def task_instance(self) -> RuntimeTaskInstanceProtocol:
        return self.context["ti"]

    @property
    def dag_run(self) -> TaskDAGRun:
        return TaskDAGRun(self.context["dag_run"])
