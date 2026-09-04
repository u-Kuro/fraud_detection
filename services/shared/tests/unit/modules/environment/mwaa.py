import pytest
from _pytest.monkeypatch import MonkeyPatch
from pydantic import ValidationError

from services.shared.src.modules.environment.mwaa import MWAAEnvironment

def test_mwaa_environment_name_value(monkeypatch: MonkeyPatch):
    value = "value"
    monkeypatch.setenv("MWAA_ENVIRONMENT_NAME", value)

    from services.shared.src.modules.environment.mwaa import mwaa_environment

    assert mwaa_environment.MWAA_ENVIRONMENT_NAME == value

def test_mwaa_environment_with_missing_environment(monkeypatch: MonkeyPatch):
    monkeypatch.delenv("MWAA_ENVIRONMENT_NAME", raising=False)

    with pytest.raises(ValidationError):
        MWAAEnvironment()