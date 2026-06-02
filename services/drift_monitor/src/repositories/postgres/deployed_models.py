from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import text

from services.drift_monitor.src.repositories.postgres import engine

def get_latest_dataset_max_date() -> Optional[datetime]:
    with engine.connect() as connection:
        dataset_max_date = connection.execute(text("""
            SELECT MAX(dataset_max_date) FROM deployed_models
            WHERE status = 'active'
        """)).scalar()
    return (
        dataset_max_date.astimezone(timezone.utc)
        if dataset_max_date
        else None
    )

def has_any_active_deployed_model() -> bool:
    with engine.connect() as connection:
        count = connection.execute(text("""
            SELECT COUNT(*) FROM deployed_models
            WHERE status = 'active'
        """)).scalar()
    return (count or 0) > 0