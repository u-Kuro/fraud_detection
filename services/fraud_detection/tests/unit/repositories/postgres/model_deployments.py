from unittest.mock import MagicMock
from uuid import uuid4

from services.fraud_detection.src.modules.schemas.mlflow import DeployedModel
from services.fraud_detection.src.repositories.postgres.model_deployments import get_active_model_deployment

def make_session_mock(name: str, version: int):
    mock_row = MagicMock()
    mock_row.t = (name, version)
    mock_result = MagicMock()
    mock_result.one.return_value = mock_row
    mock_inner = MagicMock()
    mock_inner.execute.return_value = mock_result
    mock_ctx = MagicMock()
    mock_ctx.__enter__ = MagicMock(return_value=mock_inner)
    mock_ctx.__exit__ = MagicMock(return_value=False)
    mock_sm = MagicMock()
    mock_sm.begin.return_value = mock_ctx
    return mock_sm

def test_get_active_model_deployment_returns_deployed_model(mocker):
    mocker.patch(
        "services.fraud_detection.src.repositories.postgres.model_deployments.sql_session",
        make_session_mock("xgboost", 7),
    )
    mocker.patch(
        "services.fraud_detection.src.repositories.postgres.model_deployments.PostgresConfig"
    ).project_id.return_value = uuid4()

    result = get_active_model_deployment()
    assert isinstance(result, DeployedModel)

def test_get_active_model_deployment_returns_correct_name(mocker):
    mocker.patch(
        "services.fraud_detection.src.repositories.postgres.model_deployments.sql_session",
        make_session_mock("xgboost", 7),
    )
    mocker.patch(
        "services.fraud_detection.src.repositories.postgres.model_deployments.PostgresConfig"
    ).project_id.return_value = uuid4()

    result = get_active_model_deployment()
    assert result.model_name == "xgboost"

def test_get_active_model_deployment_returns_correct_version(mocker):
    mocker.patch(
        "services.fraud_detection.src.repositories.postgres.model_deployments.sql_session",
        make_session_mock("xgboost", 7),
    )
    mocker.patch(
        "services.fraud_detection.src.repositories.postgres.model_deployments.PostgresConfig"
    ).project_id.return_value = uuid4()

    result = get_active_model_deployment()
    assert result.model_version == 7
