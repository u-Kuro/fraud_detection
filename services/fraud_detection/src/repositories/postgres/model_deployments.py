from sqlalchemy import select

from services.fraud_detection.src.modules.schemas.mlflow import DeployedModel
from services.fraud_detection.src.repositories.postgres.postgres import sql_session
from services.shared.src.modules.configs.postgres import PostgresConfig
from services.shared.src.modules.schemas.postgres.model_deployments import ModelDeployments

def get_active_model_deployment() -> DeployedModel:
    with sql_session.begin() as session:
        (name, version) = session.execute(
            select(
                ModelDeployments.name,
                ModelDeployments.version
            )
            .where(
                ModelDeployments.project_id == PostgresConfig.project_id(),
                ModelDeployments.active.is_(True),
            )
            .limit(1)
        ).one().t

    return DeployedModel(
        model_name=name,
        model_version=version
    )