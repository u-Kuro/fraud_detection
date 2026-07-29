from uuid import UUID

from pydantic import validate_call

from dags.shared.modules.schemas.postgres.postgres import PostgresTableKeys
from dags.shared.modules.schemas.postgres.projects import ProjectsColumnKeys
from dags.shared.repositories.postgres.postgres import postgres_hook

@validate_call(validate_return=True)
def get_project_id(project_name: str) -> UUID:
    project_id_row = postgres_hook.get_first(f"""
        SELECT {ProjectsColumnKeys.id}
        FROM {PostgresTableKeys.projects}
        WHERE {ProjectsColumnKeys.name} = %({ProjectsColumnKeys.name})s
        """, {
            ProjectsColumnKeys.name: project_name
        }
    )

    if project_id_row is None:
        raise ValueError(f"Project {project_name!r} not found.")

    return project_id_row[0]