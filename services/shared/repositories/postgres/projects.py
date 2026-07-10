from uuid import UUID

from sqlalchemy import text

from services.shared.repositories.postgres import engine

def get_project_id(project_name: str) -> UUID:
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT id 
            FROM ml_projects 
            WHERE project_name = :project_name
        """), {
            "project_name": project_name}
        )
        return UUID(result.scalar_one())