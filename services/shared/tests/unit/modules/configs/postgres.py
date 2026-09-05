from uuid import uuid4, UUID

from pytest_mock import MockerFixture

from services.shared.src.modules.configs.postgres import PostgresConfig

def test_postgres_config_values(mocker: MockerFixture):
    value = uuid4()
    mocker.patch(
        target="services.shared.src.modules.configs.postgres.get_project_id",
        return_value=value,
    )
    PostgresConfig.project_id.cache_clear()

    result = PostgresConfig.project_id()

    assert isinstance(result, UUID)
    assert result == value