import pytest
from pydantic import ValidationError

from services.drift_check.src.modules.environment.drift_check import DriftCheckEnvironment

def test_drift_check_environment_reads_run_id(monkeypatch):
    monkeypatch.setenv("ACTIVE_MODEL_DEPLOYMENT_MLFLOW_RUN_ID", "run-abc-123")
    env = DriftCheckEnvironment()
    assert env.ACTIVE_MODEL_DEPLOYMENT_MLFLOW_RUN_ID == "run-abc-123"

def test_drift_check_environment_missing_run_id_raises(monkeypatch):
    monkeypatch.delenv("ACTIVE_MODEL_DEPLOYMENT_MLFLOW_RUN_ID", raising=False)
    with pytest.raises(ValidationError):
        DriftCheckEnvironment()

def test_drift_check_environment_module_level_instance():
    from services.drift_check.src.modules.environment.drift_check import drift_check_environment
    assert isinstance(drift_check_environment, DriftCheckEnvironment)
    assert drift_check_environment.ACTIVE_MODEL_DEPLOYMENT_MLFLOW_RUN_ID == "test-run-id-000000000000"
