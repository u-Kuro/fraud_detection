from services.shared.src.modules.environment.postgres import PostgresEnvironment

def test_postgres_environment_instance():
    from services.shared.src.modules.environment.postgres import postgres_environment

    assert isinstance(postgres_environment, PostgresEnvironment)

def test_postgres_environment_values():
    from services.shared.src.modules.environment.postgres import postgres_environment

    assert isinstance(postgres_environment.DATABASE_URL, str)