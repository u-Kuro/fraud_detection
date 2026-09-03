from unittest.mock import MagicMock

from services.fraud_detection.src.modules.schemas.mlflow import DeployedModel

def test_mlflow_model_stores_deployed_model(mocker):
    mocker.patch("services.fraud_detection.src.repositories.mlflow.models.mlflow")
    from services.fraud_detection.src.repositories.mlflow.models import MlflowModel
    dm = DeployedModel(model_name="xgboost", model_version=1)
    m = MlflowModel(deployed_model=dm)
    assert m.deployed_model is dm

def test_mlflow_model_loads_model_from_uri(mocker):
    mock_mlflow = mocker.patch("services.fraud_detection.src.repositories.mlflow.models.mlflow")
    from services.fraud_detection.src.repositories.mlflow.models import MlflowModel
    dm = DeployedModel(model_name="xgboost", model_version=3)
    MlflowModel(deployed_model=dm)
    mock_mlflow.sklearn.load_model.assert_called_once_with(model_uri="models:/xgboost/3")

def test_mlflow_model_stores_loaded_model(mocker):
    mock_mlflow = mocker.patch("services.fraud_detection.src.repositories.mlflow.models.mlflow")
    sentinel = MagicMock()
    mock_mlflow.sklearn.load_model.return_value = sentinel
    from services.fraud_detection.src.repositories.mlflow.models import MlflowModel
    dm = DeployedModel(model_name="xgboost", model_version=1)
    m = MlflowModel(deployed_model=dm)
    assert m.model is sentinel
