from uuid import uuid4

from services.shared.src.modules.configs.postgres import PostgresConfig

def test_project_id_returns_uuid(mocker):
    expected = uuid4()
    mocker.patch(
        "services.shared.modules.configs.postgres.get_project_id",
        return_value=expected,
    )
    # Clear lru_cache so the mock is called
    PostgresConfig.project_id.cache_clear()
    result = PostgresConfig.project_id()
    assert result == expected

def test_project_id_is_cached(mocker):
    expected = uuid4()
    mock_get = mocker.patch(
        "services.shared.modules.configs.postgres.get_project_id",
        return_value=expected,
    )
    PostgresConfig.project_id.cache_clear()
    PostgresConfig.project_id()
    PostgresConfig.project_id()
    mock_get.assert_called_once()

def test_project_id_uses_project_name(mocker):
    mock_get = mocker.patch(
        "services.shared.modules.configs.postgres.get_project_id",
        return_value=uuid4(),
    )
    PostgresConfig.project_id.cache_clear()
    PostgresConfig.project_id()
    mock_get.assert_called_once_with("fraud_detection")