import pytest
from pydantic import ValidationError

from services.shared.src.modules.environment.mwaa import MWAAEnvironment

def test_mwaa_environment_reads_environment_name(monkeypatch):
    monkeypatch.setenv("MWAA_ENVIRONMENT_NAME", "my-env")
    env = MWAAEnvironment()
    assert env.MWAA_ENVIRONMENT_NAME == "my-env"

def test_mwaa_environment_missing_name_raises(monkeypatch):
    monkeypatch.delenv("MWAA_ENVIRONMENT_NAME", raising=False)
    with pytest.raises(ValidationError):
        MWAAEnvironment()

def test_mwaa_environment_module_level_instance():
    from services.shared.src.modules.environment.mwaa import MWAAEnvironment, mwaa_environment
    assert isinstance(mwaa_environment, MWAAEnvironment)
    assert mwaa_environment.MWAA_ENVIRONMENT_NAME == "test-mwaa-environment"
