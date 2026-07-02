from sqlalchemy import text

from services.drift_monitor.src.repositories.postgres import engine
from shared.modules.configs import postgres_config

def has_any_active_model() -> bool:
    with engine.connect() as connection:
        has_active_model = connection.execute(text("""
            SELECT EXISTS (
                SELECT 1 FROM model_deployments
                WHERE 
                    project_id = :project_id
                AND active
            )
        """), {
            "project_id": postgres_config.PROJECT_ID
        }).scalar()
    return bool(has_active_model)