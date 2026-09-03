import pytest
from pydantic import ValidationError

from services.shared.src.modules.environment.s3 import S3Environment

def test_s3_environment_reads_bucket_name(monkeypatch):
    monkeypatch.setenv("S3_BUCKET_NAME", "my-bucket")
    env = S3Environment()
    assert env.S3_BUCKET_NAME == "my-bucket"

def test_s3_environment_missing_bucket_name_raises(monkeypatch):
    monkeypatch.delenv("S3_BUCKET_NAME", raising=False)
    with pytest.raises(ValidationError):
        S3Environment()

def test_s3_environment_module_level_instance():
    from services.shared.src.modules.environment.s3 import s3_environment
    assert isinstance(s3_environment, S3Environment)
    assert s3_environment.S3_BUCKET_NAME == "test-bucket"
