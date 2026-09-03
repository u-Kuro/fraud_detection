import dataclasses
import pytest
from dags.shared.modules.configs.s3 import S3Config

def test_s3_config_s3_mle_bucket():
    assert S3Config.S3_MLE_BUCKET == "mle"

def test_s3_config_is_frozen():
    config = S3Config()
    with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
        config.S3_MLE_BUCKET = "other"

def test_s3_config_instantiation():
    config = S3Config()
    assert config.S3_MLE_BUCKET == "mle"
