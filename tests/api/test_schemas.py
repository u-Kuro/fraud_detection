import pytest
from api.schemas import MlflowModelFlavor, MlflowModelUri, PredictionRequest
from pydantic import ValidationError

def test_prediction_request_valid(sample_prediction_request):
    request = PredictionRequest(**sample_prediction_request)
    assert request.amount == 149.99
    for i in range(1, 29):
        assert getattr(request, f"v{i}") == 0.0

def test_prediction_request_missing_feature(sample_prediction_request):
    del sample_prediction_request["v1"]
    with pytest.raises(ValidationError):
        PredictionRequest(**sample_prediction_request)

def test_timestamp_converts_to_utc(sample_prediction_request):
    request = PredictionRequest(**sample_prediction_request)
    assert request.transaction_timestamp.tzinfo is not None

def test_model_uri_alias_format():
    uri = MlflowModelUri(model_uri="models:/name@alias")
    assert uri.model_uri == "models:/name@alias"

def test_model_uri_version_format():
    uri = MlflowModelUri(model_uri="models:/name/1")
    assert uri.model_uri == "models:/name/1"

def test_model_uri_invalid_format():
    with pytest.raises(ValidationError):
        MlflowModelUri(model_uri="some-random-string")

def test_model_flavor_valid():
    mlflow_model_flavor = MlflowModelFlavor(flavor="sklearn")
    assert mlflow_model_flavor.flavor == "sklearn"

def test_model_flavor_invalid():
    with pytest.raises(ValidationError):
        MlflowModelFlavor(flavor="tensorflow")