from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import text

from services.drift_monitor.src.repositories.postgres import engine
from shared.modules.configs import postgres_config

def has_any_active_deployed_model() -> bool:
    with engine.connect() as connection:
        has_active_model = connection.execute(text("""
            SELECT EXISTS (
                SELECT 1 FROM model_deployments
                    WHERE   status        = 'active'
                        AND project_id  = :project_id
            )
        """), {
            "project_id": postgres_config.PROJECT_ID
        }).scalar()
    return bool(has_active_model)

def get_latest_dataset_max_date() -> Optional[datetime]:
    with engine.connect() as connection:
        dataset_max_date = connection.execute(text("""
            SELECT MAX(dataset_max_date)
            FROM model_deployments
                WHERE   status      = 'active'
                    AND project_id  = :project_id
        """)).scalar()

    if isinstance(dataset_max_date, datetime):
        return dataset_max_date.astimezone(timezone.utc)
    else:
        return None