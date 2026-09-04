from pydantic_settings import BaseSettings, SettingsConfigDict

class PostgresEnvironment(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    # PGHOST: StrictStr
    # PGPORT: int
    # PGDATABASE: StrictStr
    # PGUSER: StrictStr
    # PGPASSWORD: StrictStr

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg2://" # {self.PGUSER}:{self.PGPASSWORD}@{self.PGHOST}:{self.PGPORT}/{self.PGDATABASE}"

postgres_environment = PostgresEnvironment()