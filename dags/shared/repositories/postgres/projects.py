from uuid import UUID

from dags.shared.repositories.postgres import postgres_hook

def get_project_id(project_name: str) -> UUID:
    project_id_row = postgres_hook.get_first("""
        SELECT id
        FROM ml_projects
        WHERE project_name = %(project_name)s
        """, {
            "project_name": project_name
        }
    )

    if project_id_row is None:
        raise ValueError(f"Project '{project_name}' not found.")

    return UUID(project_id_row[0])