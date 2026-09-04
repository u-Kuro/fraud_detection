def test_postgres_environment_database_url_is_string():
    from services.shared.src.modules.environment.postgres import postgres_environment

    assert isinstance(postgres_environment.DATABASE_URL, str)

