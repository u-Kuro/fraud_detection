from sqlalchemy import text

from services.fraud_detection.src.modules.schemas.mlflow import DeployedModel
from services.fraud_detection.src.repositories.postgres.postgres import engine
from services.shared.modules.configs.postgres import PostgresConfig
from services.shared.modules.schemas.postgres.model_deployments import ModelDeploymentsColumnKeys
from services.shared.modules.schemas.postgres.postgres import PostgresTableKeys

def get_active_model_deployment() -> DeployedModel:
    with engine.connect() as connection:
        row = connection.execute(text(f"""
            SELECT
                {ModelDeploymentsColumnKeys.name},
                {ModelDeploymentsColumnKeys.version}
            FROM {PostgresTableKeys.model_deployments}
            WHERE
                {ModelDeploymentsColumnKeys.project_id} = :{ModelDeploymentsColumnKeys.project_id}
            AND {ModelDeploymentsColumnKeys.active}
            LIMIT 1
            """), {
                ModelDeploymentsColumnKeys.project_id: PostgresConfig.PROJECT_ID()
            }
        ).fetchone()

    if row is None:
        raise ValueError(f"No active model deployment found.")

    assert isinstance(row.name, str)
    assert isinstance(row.version, int)

    return DeployedModel(
        model_name=row.name,
        model_version=row.version
    )