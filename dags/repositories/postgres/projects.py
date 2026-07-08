from uuid import UUID

from airflow.providers.postgres.hooks.postgres import PostgresHook

from dags.modules.configs.dags import dags_config

def get_project_id(project_name: str) -> UUID:
    hook = PostgresHook(postgres_conn_id=dags_config.SLACK_CONNECTION_ID)
    project_id_row = hook.get_first("""
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