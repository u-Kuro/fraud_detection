import pytest
from pydantic import ValidationError
from dags.shared.modules.environment.ecr import ECREnvironment

def test_ecr_environment_reads_drift_check_image(monkeypatch):
    monkeypatch.setenv("DRIFT_CHECK_IMAGE", "123.dkr.ecr.us-east-1.amazonaws.com/drift:v1")
    env = ECREnvironment()
    assert "drift" in env.DRIFT_CHECK_IMAGE

def test_ecr_environment_reads_train_model_image(monkeypatch):
    monkeypatch.setenv("TRAIN_MODEL_IMAGE", "123.dkr.ecr.us-east-1.amazonaws.com/train:v1")
    env = ECREnvironment()
    assert "train" in env.TRAIN_MODEL_IMAGE

def test_ecr_environment_reads_archive_image(monkeypatch):
    monkeypatch.setenv("ARCHIVE_IMAGE", "123.dkr.ecr.us-east-1.amazonaws.com/archive:v1")
    env = ECREnvironment()
    assert "archive" in env.ARCHIVE_IMAGE

def test_ecr_environment_missing_drift_check_image_raises(monkeypatch):
    monkeypatch.delenv("DRIFT_CHECK_IMAGE", raising=False)
    with pytest.raises(ValidationError):
        ECREnvironment()

def test_ecr_environment_missing_train_model_image_raises(monkeypatch):
    monkeypatch.delenv("TRAIN_MODEL_IMAGE", raising=False)
    with pytest.raises(ValidationError):
        ECREnvironment()

def test_ecr_environment_missing_archive_image_raises(monkeypatch):
    monkeypatch.delenv("ARCHIVE_IMAGE", raising=False)
    with pytest.raises(ValidationError):
        ECREnvironment()

def test_ecr_environment_module_level_instance():
    from dags.shared.modules.environment.ecr import ecr_environment
    assert isinstance(ecr_environment, ECREnvironment)
