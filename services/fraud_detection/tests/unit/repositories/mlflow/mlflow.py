from mlflow import MlflowClient
from services.fraud_detection.src.repositories.mlflow.mlflow import client

def test_client_is_mlflow_client():
    assert isinstance(client, MlflowClient)

def test_client_is_not_none():
    assert client is not None
