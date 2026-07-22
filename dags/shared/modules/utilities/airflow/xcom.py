from enum import StrEnum
from itertools import product
from typing import Sequence, Type, Any

from airflow.sdk.types import TaskInstance

def build_task_id(segments: Sequence[str]) -> str:
    return ".".join(segments)

def build_task_ids(segments: Sequence[str | Type[StrEnum] | set[str]]) -> list[str]:
    options: list[list[str]] = []
    for segment in segments:
        if isinstance(segment, type) and issubclass(segment, StrEnum):
            options.append([member.value for member in segment])
        else:
            options.append([str(segment)])

    return [".".join(combo) for combo in product(*options)]

def xcom_pull_coalesce(ti: TaskInstance, task_id_segments: Sequence[str | Type[StrEnum] | set[str]], key: str) -> Any:
    values = ti.xcom_pull(task_ids=build_task_ids(task_id_segments), key=key)
    return next((v for v in values if v is not None), None)