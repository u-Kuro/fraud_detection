import pytest
from pydantic import ValidationError
from dags.shared.modules.environment.s3 import S3Environment

def test_s3_environment_reads_connection_id(monkeypatch):
    monkeypatch.setenv("AIRFLOW_VAR_S3_CONNECTION_ID", "s3_conn")
    monkeypatch.setenv("AIRFLOW_VAR_S3_BUCKET", "my-bucket")
    env = S3Environment()
    assert env.S3_CONNECTION_ID == "s3_conn"
    assert env.S3_BUCKET == "my-bucket"

def test_s3_environment_missing_bucket_raises(monkeypatch):
    monkeypatch.setenv("AIRFLOW_VAR_S3_CONNECTION_ID", "s3_conn")
    monkeypatch.delenv("AIRFLOW_VAR_S3_BUCKET", raising=False)
    with pytest.raises(ValidationError):
        S3Environment()

def test_s3_environment_module_level_instance():
    from dags.shared.modules.environment.s3 import s3_environment
    assert isinstance(s3_environment, S3Environment)
