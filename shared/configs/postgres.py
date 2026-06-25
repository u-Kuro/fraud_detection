from pydantic import BaseModel, ConfigDict

class PostgresConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    POSTGRES_DB_URL: str = "postgresql+psycopg2://"

postgres_config = PostgresConfig()
