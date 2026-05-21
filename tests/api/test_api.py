import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

import api.main


@pytest.fixture
def client(sample_prediction_request, mock_mlflow_model_legitimate):
    from api.schemas import (
        TransactionInference, PredictionRequest,
    )

    mock_predictor = MagicMock()
    mock_predictor.model_uri = "models:/name@alias"
    mock_predictor.model_version = 1

    request = PredictionRequest(**sample_prediction_request)
    mock_predictor.predict.return_value = TransactionInference(
        **request.model_dump(),
        is_fraud=None,
        is_fraud_probability=0.05,
        is_fraud_prediction=False,
        model_name="name",
        model_version=1,
        latency_ms=1.5,
    )

    mock_monitor = MagicMock()

    with patch("api.main.ModelPredictor", return_value=mock_predictor), \
     patch("api.main.InferenceLogger", return_value=mock_monitor):
        from api.main import app

        with TestClient(app) as client:
            yield client

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_predict_endpoint(client, sample_prediction_request):
    response = client.post("/predict", json=sample_prediction_request)
    assert response.status_code == 200
    body = response.json()
    assert "is_fraud_prediction" in body
    assert "is_fraud_probability" in body

    assert "amount" not in body
    assert "transaction_id" not in body
    assert "is_fraud" not in body
    assert "model_name" not in body

def test_predict_missing_field_returns_422(client, sample_prediction_request):
    del sample_prediction_request["amount"]
    response = client.post("/predict", json=sample_prediction_request)
    assert response.status_code == 422

