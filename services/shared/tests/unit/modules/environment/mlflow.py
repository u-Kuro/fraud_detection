import pytest
from _pytest.monkeypatch import MonkeyPatch
from pydantic import ValidationError

from services.shared.src.modules.environment.mlflow import MLflowEnvironment

def test_mlflow_environment_workspace_value(monkeypatch: MonkeyPatch):
    value = "value"
    monkeypatch.setenv("MLFLOW_WORKSPACE", value)
    
    from services.shared.src.modules.environment.mlflow import mlflow_environment
    
    assert mlflow_environment.MLFLOW_WORKSPACE == value

def test_mlflow_environment_with_missing_environment(monkeypatch: MonkeyPatch):
    monkeypatch.delenv("MLFLOW_WORKSPACE", raising=False)

    with pytest.raises(ValidationError):
        MLflowEnvironment()