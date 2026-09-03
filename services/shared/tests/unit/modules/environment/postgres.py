from services.shared.src.modules.environment.postgres import PostgresEnvironment

def test_postgres_environment_instantiation():
    # All fields are commented out — no required fields
    env = PostgresEnvironment()
    assert env is not None

def test_postgres_environment_database_url_is_string():
    env = PostgresEnvironment()
    assert isinstance(env.DATABASE_URL, str)

def test_postgres_environment_database_url_starts_with_postgresql():
    env = PostgresEnvironment()
    assert env.DATABASE_URL.startswith("postgresql+psycopg2://")

def test_postgres_environment_module_level_instance():
    from services.shared.src.modules.environment.postgres import postgres_environment
    assert isinstance(postgres_environment, PostgresEnvironment)
