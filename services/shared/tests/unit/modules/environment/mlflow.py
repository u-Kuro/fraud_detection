import pytest
from pydantic import ValidationError

from services.shared.src.modules.environment.mlflow import MLflowEnvironment

def test_mlflow_environment_reads_workspace(monkeypatch):
    monkeypatch.setenv("MLFLOW_WORKSPACE", "my_workspace")
    env = MLflowEnvironment()
    assert env.MLFLOW_WORKSPACE == "my_workspace"

def test_mlflow_environment_missing_workspace_raises(monkeypatch):
    monkeypatch.delenv("MLFLOW_WORKSPACE", raising=False)
    with pytest.raises(ValidationError):
        MLflowEnvironment()

def test_mlflow_environment_module_level_instance():
    from services.shared.src.modules.environment.mlflow import mlflow_environment
    assert isinstance(mlflow_environment, MLflowEnvironment)
    assert mlflow_environment.MLFLOW_WORKSPACE == "test_workspace"
