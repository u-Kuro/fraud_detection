import pytest
from _pytest.monkeypatch import MonkeyPatch
from pydantic import ValidationError

from services.shared.src.modules.environment.s3 import S3Environment

def test_s3_environment_instance():
    from services.shared.src.modules.environment.s3 import s3_environment

    assert isinstance(s3_environment, S3Environment)

def test_s3_environment_values(monkeypatch: MonkeyPatch):
    value = "value"
    monkeypatch.setenv(
        name="S3_BUCKET_NAME",
        value=value
    )

    environment = S3Environment()

    assert isinstance(environment.S3_BUCKET_NAME, str)
    assert environment.S3_BUCKET_NAME == value

def test_s3_environment_failure_with_missing_environment(monkeypatch: MonkeyPatch):
    monkeypatch.delenv(
        name="S3_BUCKET_NAME",
        raising=False
    )

    with pytest.raises(ValidationError):
        S3Environment()