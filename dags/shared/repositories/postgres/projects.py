from uuid import UUID

from pydantic import validate_call
from sqlalchemy import select

from dags.shared.modules.schemas.postgres.projects import Projects
from dags.shared.repositories.postgres.postgres import sql_session

@validate_call(validate_return=True)
def get_project_id(project_name: str) -> UUID:
    with sql_session.begin() as session:
        (project_id,) = session.execute(
            select(Projects.id)
            .where(Projects.name == project_name)
        ).one().t

    return project_id