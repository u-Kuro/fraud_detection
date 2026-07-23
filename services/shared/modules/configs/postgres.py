from dataclasses import dataclass
from functools import lru_cache
from uuid import UUID

from services.shared.repositories.postgres import get_project_id

@dataclass(frozen=True)
class PostgresConfig:

    POSTGRES_DB_URL: str = "postgresql+psycopg2://"
    PROJECT_NAME: str = "fraud-detection"

    @lru_cache(maxsize=None)
    def PROJECT_ID(self) -> UUID:
        return get_project_id(self.PROJECT_NAME)
