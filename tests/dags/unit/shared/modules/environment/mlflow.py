import pytest
from pydantic import ValidationError
from dags.shared.modules.environment.mlflow import MLflowEnvironment

def test_mlflow_environment_reads_tracking_uri(monkeypatch):
    monkeypatch.setenv("AIRFLOW_VAR_MLFLOW_TRACKING_URI", "http://mlflow:5000")
    monkeypatch.setenv("AIRFLOW_VAR_MLFLOW_TRACKING_USERNAME", "u")
    monkeypatch.setenv("AIRFLOW_VAR_MLFLOW_TRACKING_PASSWORD", "p")
    monkeypatch.setenv("AIRFLOW_VAR_MLFLOW_WORKSPACE", "ws")
    env = MLflowEnvironment()
    assert env.MLFLOW_TRACKING_URI == "http://mlflow:5000"

def test_mlflow_environment_missing_workspace_raises(monkeypatch):
    monkeypatch.setenv("AIRFLOW_VAR_MLFLOW_TRACKING_URI", "http://mlflow:5000")
    monkeypatch.setenv("AIRFLOW_VAR_MLFLOW_TRACKING_USERNAME", "u")
    monkeypatch.setenv("AIRFLOW_VAR_MLFLOW_TRACKING_PASSWORD", "p")
    monkeypatch.delenv("AIRFLOW_VAR_MLFLOW_WORKSPACE", raising=False)
    with pytest.raises(ValidationError):
        MLflowEnvironment()

def test_mlflow_environment_module_level_instance():
    from dags.shared.modules.environment.mlflow import mlflow_environment
    assert isinstance(mlflow_environment, MLflowEnvironment)
