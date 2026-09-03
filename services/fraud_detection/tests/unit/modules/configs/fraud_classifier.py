import dataclasses

import pytest

from services.fraud_detection.src.modules.configs.fraud_classifier import FraudClassifierConfig
from services.fraud_detection.src.modules.schemas.mlflow import DeployedModel

def test_fraud_classifier_config_default_threshold():
    assert FraudClassifierConfig.classification_threshold == 0.5

def test_fraud_classifier_config_is_frozen():
    config = FraudClassifierConfig()
    with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
        config.classification_threshold = 0.7

def test_deployed_model_is_cached(mocker):
    mock_model = DeployedModel(model_name="xgboost", model_version=1)
    mocker.patch(
        "services.fraud_detection.src.modules.configs.fraud_classifier.get_active_model_deployment",
        return_value=mock_model,
    )
    FraudClassifierConfig.deployed_model.cache_clear()
    result1 = FraudClassifierConfig.deployed_model()
    result2 = FraudClassifierConfig.deployed_model()
    assert result1 is result2

def test_deployed_model_calls_get_active_deployment(mocker):
    mock_model = DeployedModel(model_name="xgboost", model_version=2)
    mock_get = mocker.patch(
        "services.fraud_detection.src.modules.configs.fraud_classifier.get_active_model_deployment",
        return_value=mock_model,
    )
    FraudClassifierConfig.deployed_model.cache_clear()
    FraudClassifierConfig.deployed_model()
    mock_get.assert_called_once()
