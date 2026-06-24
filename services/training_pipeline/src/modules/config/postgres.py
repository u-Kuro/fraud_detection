from pydantic import BaseModel

class PostgresConfig(BaseModel):
    POSTGRES_DB_URL: str = "postgresql+psycopg2://"

postgres_config = PostgresConfig()
