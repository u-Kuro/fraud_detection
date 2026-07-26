from sqlalchemy import text

from services.fraud_detection.src.modules.schemas import DeployedModel
from services.fraud_detection.src.repositories.postgres import engine
from services.shared.modules.configs import PostgresConfig

def get_active_model_deployment() -> DeployedModel:
    with engine.connect() as connection:
        row = connection.execute(text("""
            SELECT name, version
            FROM model_deployments
            WHERE
                project_id = :project_id
            AND active
            LIMIT 1
            """), {
                "project_id": PostgresConfig.PROJECT_ID()
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