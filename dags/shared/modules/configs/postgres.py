from dataclasses import dataclass
from functools import lru_cache
from uuid import UUID

from dags.shared.modules.configs.project import ProjectConfig
from dags.shared.repositories.postgres.projects import get_project_id

@dataclass(frozen=True)
class PostgresConfig:
    @classmethod
    @lru_cache(maxsize=None)
    def project_id(cls) -> UUID:
        return get_project_id(ProjectConfig.project_name)
