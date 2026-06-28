from uuid import UUID

from pydantic import BaseModel, ConfigDict, computed_field

from shared.repositories.postgres import get_project_id

class PostgresConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    POSTGRES_DB_URL: str = "postgresql+psycopg2://"
    PROJECT_NAME: str = "fraud-detection"

    @computed_field
    @property
    def PROJECT_ID(self) -> UUID:
        return get_project_id(self.PROJECT_NAME)

postgres_config = PostgresConfig()
