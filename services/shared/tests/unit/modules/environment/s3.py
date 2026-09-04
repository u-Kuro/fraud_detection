import pytest
from _pytest.monkeypatch import MonkeyPatch
from pydantic import ValidationError

from services.shared.src.modules.environment.s3 import S3Environment

def test_s3_environment_bucket_name_value(monkeypatch: MonkeyPatch):
    value = "value"
    monkeypatch.setenv("S3_BUCKET_NAME", value)

    from services.shared.src.modules.environment.s3 import s3_environment

    assert s3_environment.S3_BUCKET_NAME == value

def test_s3_environment_with_missing_environment(monkeypatch: MonkeyPatch):
    monkeypatch.delenv("S3_BUCKET_NAME", raising=False)

    with pytest.raises(ValidationError):
        S3Environment()