import pytest
from _pytest.monkeypatch import MonkeyPatch
from pydantic import ValidationError

from services.drift_check.src.modules.environment.drift_check import DriftCheckEnvironment

def test_drift_check_environment_instance():
    from services.drift_check.src.modules.environment.drift_check import drift_check_environment

    assert isinstance(drift_check_environment, DriftCheckEnvironment)

def test_drift_check_environment_values(monkeypatch: MonkeyPatch):
    value = "value"
    monkeypatch.setenv(
        name="ACTIVE_MODEL_DEPLOYMENT_MLFLOW_RUN_ID",
        value=value
    )

    environment = DriftCheckEnvironment()

    assert isinstance(environment.ACTIVE_MODEL_DEPLOYMENT_MLFLOW_RUN_ID, str)
    assert environment.ACTIVE_MODEL_DEPLOYMENT_MLFLOW_RUN_ID == value

def test_drift_check_environment_failure_with_missing_environment(monkeypatch: MonkeyPatch):
    monkeypatch.delenv(
        name="ACTIVE_MODEL_DEPLOYMENT_MLFLOW_RUN_ID",
        raising=False
    )

    with pytest.raises(ValidationError):
        DriftCheckEnvironment()