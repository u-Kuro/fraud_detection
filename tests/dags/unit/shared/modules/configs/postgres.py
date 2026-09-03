from uuid import uuid4
from dags.shared.modules.configs.postgres import PostgresConfig

def test_project_id_returns_uuid(mocker):
    expected = uuid4()
    mocker.patch(
        "dags.shared.modules.configs.postgres.get_project_id",
        return_value=expected,
    )
    PostgresConfig.project_id.cache_clear()
    result = PostgresConfig.project_id()
    assert result == expected

def test_project_id_is_cached(mocker):
    expected = uuid4()
    mock_fn = mocker.patch(
        "dags.shared.modules.configs.postgres.get_project_id",
        return_value=expected,
    )
    PostgresConfig.project_id.cache_clear()
    PostgresConfig.project_id()
    PostgresConfig.project_id()
    mock_fn.assert_called_once()

def test_project_id_uses_fraud_detection_name(mocker):
    mock_fn = mocker.patch(
        "dags.shared.modules.configs.postgres.get_project_id",
        return_value=uuid4(),
    )
    PostgresConfig.project_id.cache_clear()
    PostgresConfig.project_id()
    mock_fn.assert_called_once_with("fraud_detection")
