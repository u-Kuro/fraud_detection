from sqlalchemy import text

from services.drift_check.src.repositories.postgres import engine
from services.shared.modules.configs import PostgresConfig

def get_active_model_deployment_mlflow_run_id() -> str:
    with engine.connect() as connection:
        row = connection.execute(text("""
            SELECT mlflow_run_id
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

    assert isinstance(row.mlflow_run_id, str)

    return row.mlflow_run_id