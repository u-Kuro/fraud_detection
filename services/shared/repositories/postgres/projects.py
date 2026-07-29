from uuid import UUID

from sqlalchemy import text

from services.shared.modules.schemas.postgres.postgres import PostgresTableKeys
from services.shared.modules.schemas.postgres.projects import ProjectsColumnKeys
from services.shared.repositories.postgres import engine

def get_project_id(project_name: str) -> UUID:
    with engine.connect() as connection:
        result = connection.execute(text(f"""
            SELECT {ProjectsColumnKeys.id}
            FROM {PostgresTableKeys.projects} 
            WHERE {ProjectsColumnKeys.name} = :{ProjectsColumnKeys.name}
            LIMIT 1
        """), {
                ProjectsColumnKeys.name: project_name
            }
        )
        return UUID(result.scalar_one())