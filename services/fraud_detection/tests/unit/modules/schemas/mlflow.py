import pytest
from pydantic import ValidationError

from services.fraud_detection.src.modules.schemas.mlflow import DeployedModel

def test_deployed_model_instantiation():
    model = DeployedModel(model_name="xgboost", model_version=1)
    assert model.model_name == "xgboost"
    assert model.model_version == 1

def test_deployed_model_forbids_extra_fields():
    with pytest.raises(ValidationError):
        DeployedModel(model_name="x", model_version=1, extra_field="boom")

def test_deployed_model_model_name_must_be_str():
    with pytest.raises(ValidationError):
        DeployedModel(model_name=123, model_version=1)

def test_deployed_model_model_version_must_be_int():
    with pytest.raises(ValidationError):
        DeployedModel(model_name="x", model_version="one")

def test_deployed_model_model_version_must_be_strict_int():
    with pytest.raises(ValidationError):
        # StrictInt rejects float
        DeployedModel(model_name="x", model_version=1.0)
