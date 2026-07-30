from uuid import UUID

from sqlalchemy import select

from services.shared.modules.schemas.postgres.projects import Projects
from services.shared.repositories.postgres.postgres import sql_session

def get_project_id(project_name: str) -> UUID:
    with sql_session.begin() as session:
        (project_id,) = session.execute(
            select(Projects.id)
            .where(Projects.name == project_name)
            .limit(1)
        ).one().t

        return project_id