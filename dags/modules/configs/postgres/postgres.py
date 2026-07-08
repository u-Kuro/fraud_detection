from functools import cached_property
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from dags.repositories.postgres.projects import get_project_id

class PostgresConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    POSTGRES_CONNECTION_ID: str = "mle_postgres"
    PROJECT_NAME: str = "fraud-detection"

    @cached_property
    def PROJECT_ID(self) -> UUID:
        return get_project_id(self.PROJECT_NAME)

postgres_config = PostgresConfig()
