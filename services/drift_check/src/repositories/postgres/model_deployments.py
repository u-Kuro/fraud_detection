from sqlalchemy import text

from services.drift_check.src.repositories.postgres import engine
from services.shared.modules.configs import PostgresConfig
from services.shared.modules.schemas.postgres.model_deployments import ModelDeploymentsColumnKeys
from services.shared.modules.schemas.postgres.postgres import PostgresTableKeys


def get_active_model_deployment_mlflow_run_id() -> str:
    with engine.connect() as connection:
        row = connection.execute(text(f"""
            SELECT {ModelDeploymentsColumnKeys.mlflow_run_id}
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

    assert isinstance(row.mlflow_run_id, str)

    return row.mlflow_run_id