from sqlalchemy import select

from services.drift_check.src.repositories.postgres.postgres import sql_session
from services.shared.modules.configs.postgres import PostgresConfig
from services.shared.modules.schemas.postgres.model_deployments import ModelDeployments

def get_active_model_deployment_mlflow_run_id() -> str:
    with sql_session.begin() as session:
        (mlflow_run_id, ) = session.execute(
            select(ModelDeployments.mlflow_run_id)
            .where(
                ModelDeployments.project_id == PostgresConfig.project_id(),
                ModelDeployments.active.is_(True)
            )
            .limit(1)
        ).one().t

    return mlflow_run_id