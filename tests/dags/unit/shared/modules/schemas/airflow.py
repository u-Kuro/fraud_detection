import pytest
from unittest.mock import MagicMock

from dags.shared.modules.schemas.airflow import TaskContext, TaskDAGRun

def make_airflow_context(exception=None):
    ti = MagicMock()
    ti.task_id = "my_task"
    ti.log_url = "http://localhost/log"
    ti.run_id = "run-001"
    dag_run = MagicMock()
    dag_run.conf = {"key": "val"}
    ctx = MagicMock()
    ctx.__getitem__ = MagicMock(
        side_effect=lambda k: {"ti": ti, "dag_run": dag_run, "exception": exception}[k]
    )
    return ctx

def test_task_context_exposes_exception():
    ctx = make_airflow_context(exception=ValueError("fail"))
    tc = TaskContext(ctx)
    assert isinstance(tc.exception, ValueError)

def test_task_context_exposes_task_instance():
    ctx = make_airflow_context()
    tc = TaskContext(ctx)
    assert tc.task_instance.task_id == "my_task"

def test_task_context_resolve_task_id_simple():
    ctx = make_airflow_context()
    ctx.__getitem__ = MagicMock(
        side_effect=lambda k: {"ti": MagicMock(task_id="top_task"), "dag_run": MagicMock(), "exception": None}[k]
    )
    tc = TaskContext(ctx)
    assert tc.resolve_task_id("sub") == "sub"

def test_task_context_resolve_task_id_with_group():
    ctx = make_airflow_context()
    ti = MagicMock()
    ti.task_id = "group.current_task"
    ctx.__getitem__ = MagicMock(
        side_effect=lambda k: {"ti": ti, "dag_run": MagicMock(), "exception": None}[k]
    )
    tc = TaskContext(ctx)
    assert tc.resolve_task_id("sub") == "group.sub"

def test_task_dag_run_conf_returns_dict():
    dag_run = MagicMock()
    dag_run.conf = {"a": 1}
    tdr = TaskDAGRun(dag_run)
    assert tdr.conf == {"a": 1}

def test_task_dag_run_conf_raises_type_error_when_none():
    dag_run = MagicMock()
    dag_run.conf = None
    tdr = TaskDAGRun(dag_run)
    with pytest.raises(TypeError):
        _ = tdr.conf