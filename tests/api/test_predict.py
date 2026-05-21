import time
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from api.schemas import MlflowModelFlavor, MlflowModelUri, PredictionRequest
from api.predict import ModelPredictor

@pytest.fixture
def model_predictor_legitimate(mock_mlflow_model_legitimate):
    uri = MlflowModelUri(model_uri="models:/name@alias")
    flavor = MlflowModelFlavor(flavor="sklearn")

    with patch("mlflow.sklearn.load_model", return_value=mock_mlflow_model_legitimate), \
    patch.object(ModelPredictor, "_get_model_info") as mock_info:
        from api.schemas import DeployedModel

        mock_info.return_value = DeployedModel(model_name="name", model_version=1)
        model_predictor = ModelPredictor(model_uri=uri, flavor=flavor)

    return model_predictor

@pytest.fixture
def model_predictor_fraud(mock_mlflow_model_fraud):
    uri = MlflowModelUri(model_uri="models:/name@alias")
    flavor = MlflowModelFlavor(flavor="sklearn")

    with patch("mlflow.sklearn.load_model", return_value=mock_mlflow_model_fraud), \
    patch.object(ModelPredictor, "_get_model_info") as mock_info:
        from api.schemas import DeployedModel

        mock_info.return_value = DeployedModel(model_name="name", model_version=1)
        model_predictor = ModelPredictor(model_uri=uri, flavor=flavor)

    return model_predictor

def test_predict_returns_transaction_inference(model_predictor_legitimate, sample_prediction_request):
    request = PredictionRequest(**sample_prediction_request)
    result = model_predictor_legitimate.predict(request=request, start_time=time.perf_counter())

    assert result.model_name == "name"
    assert result.model_version == 1

    assert result.is_fraud_prediction == False
    assert result.is_fraud_probability == 0.05
    assert result.latency_ms >= 0

    assert result.is_fraud is None

    assert result.amount == 149.99
    for i in range(1, 29):
        assert getattr(result, f"v{i}") == 0.0

def test_predict_fraud_case(
    model_predictor_fraud,
    sample_prediction_request
):
    request = PredictionRequest(**sample_prediction_request)
    result = model_predictor_fraud.predict(request=request, start_time=time.perf_counter())

    assert result.model_name == "name"
    assert result.model_version == 1

    assert result.is_fraud_prediction == True
    assert result.is_fraud_probability == 0.95
    assert result.latency_ms >= 0

    assert result.is_fraud is None

    assert result.amount == 149.99
    for i in range(1, 29):
        assert getattr(result, f"v{i}") == 0.0


