from services.shared.src.modules.environment.postgres import PostgresEnvironment

class TestPostgresEnvironment:
    def test_instance(self):
        from services.shared.src.modules.environment.postgres import postgres_environment

        assert isinstance(postgres_environment, PostgresEnvironment)