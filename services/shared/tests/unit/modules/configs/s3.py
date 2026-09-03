import dataclasses

import pytest

from services.shared.src.modules.configs.s3 import S3Config

def test_s3_config_model_drift_path():
    assert "fraud_detection" in S3Config.model_drift_path
    assert "drift" in S3Config.model_drift_path
    assert "xgboost" in S3Config.model_drift_path

def test_s3_config_transaction_inferences_archive_path():
    path = S3Config.transaction_inferences_archive_path
    assert "fraud_detection" in path
    assert "archive" in path
    assert "transaction_inferences" in path

def test_s3_config_instantiation():
    config = S3Config()
    assert config.model_drift_path == S3Config.model_drift_path

def test_s3_config_is_frozen():
    config = S3Config()
    with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
        config.model_drift_path = "other"
