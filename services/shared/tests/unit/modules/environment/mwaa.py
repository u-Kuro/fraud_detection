import pytest
from _pytest.monkeypatch import MonkeyPatch
from pydantic import ValidationError

from services.shared.src.modules.environment.mwaa import MWAAEnvironment


def test_mwaa_environment_instance():
    from services.shared.src.modules.environment.mwaa import mwaa_environment

    assert isinstance(mwaa_environment, MWAAEnvironment)

def test_mwaa_environment_values(monkeypatch: MonkeyPatch):
    value = "value"
    monkeypatch.setenv(
        name="MWAA_ENVIRONMENT_NAME",
        value=value
    )

    environment = MWAAEnvironment()

    assert isinstance(environment.MWAA_ENVIRONMENT_NAME, str)
    assert environment.MWAA_ENVIRONMENT_NAME == value

def test_mwaa_environment_failure_with_missing_environment(monkeypatch: MonkeyPatch):
    monkeypatch.delenv(
        name="MWAA_ENVIRONMENT_NAME",
        raising=False
    )

    with pytest.raises(ValidationError):
        MWAAEnvironment()