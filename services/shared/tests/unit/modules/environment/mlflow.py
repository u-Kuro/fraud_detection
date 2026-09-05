import pytest
from _pytest.monkeypatch import MonkeyPatch
from pydantic import ValidationError

from services.shared.src.modules.environment.mlflow import MLflowEnvironment

def test_mlflow_environment_instance():
    from services.shared.src.modules.environment.mlflow import mlflow_environment

    assert isinstance(mlflow_environment, MLflowEnvironment)

def test_mlflow_environment_values(monkeypatch: MonkeyPatch):
    value = "value"
    monkeypatch.setenv(
        name="MLFLOW_WORKSPACE",
        value=value
    )
    
    environment = MLflowEnvironment()

    assert isinstance(environment.MLFLOW_WORKSPACE, str)
    assert environment.MLFLOW_WORKSPACE == value

def test_mlflow_environment_failure_with_missing_environment(monkeypatch: MonkeyPatch):
    monkeypatch.delenv(
        name="MLFLOW_WORKSPACE",
        raising=False
    )

    with pytest.raises(ValidationError):
        MLflowEnvironment()