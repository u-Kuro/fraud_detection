import pytest
from pydantic import ValidationError
from dags.shared.modules.environment.postgres import PostgresEnvironment

def test_postgres_environment_reads_connection_id(monkeypatch):
    monkeypatch.setenv("AIRFLOW_VAR_POSTGRES_CONNECTION_ID", "pg_conn")
    env = PostgresEnvironment()
    assert env.POSTGRES_CONNECTION_ID == "pg_conn"

def test_postgres_environment_missing_connection_id_raises(monkeypatch):
    monkeypatch.delenv("AIRFLOW_VAR_POSTGRES_CONNECTION_ID", raising=False)
    with pytest.raises(ValidationError):
        PostgresEnvironment()

def test_postgres_environment_module_level_instance():
    from dags.shared.modules.environment.postgres import postgres_environment
    assert isinstance(postgres_environment, PostgresEnvironment)
