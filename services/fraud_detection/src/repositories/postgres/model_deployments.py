from sqlalchemy import select

from services.fraud_detection.src.modules.schemas.mlflow import DeployedModel
from services.fraud_detection.src.repositories.postgres.postgres import sql_session
from services.shared.modules.configs.postgres import PostgresConfig
from services.shared.modules.schemas.postgres.model_deployments import ModelDeployment

def get_active_model_deployment() -> DeployedModel:
    with sql_session.begin() as session:
        (name, version) = session.execute(
            select(
                ModelDeployment.name,
                ModelDeployment.version
            )
            .where(
                ModelDeployment.project_id == PostgresConfig.PROJECT_ID(),
                ModelDeployment.active.is_(True),
            )
            .limit(1)
        ).one().t

    return DeployedModel(
        model_name=name,
        model_version=version
    )