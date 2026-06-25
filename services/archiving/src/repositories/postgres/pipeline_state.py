from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import text
from sqlalchemy.engine import Engine

def get_archive_cutoff(engine: Engine) -> Optional[datetime]:
    """
    Returns the highest dataset_max_date across all ACTIVE deployed_models.
    Data at or before this timestamp is safe to archive.
    Returns None if no active model exists.
    """
    with engine.connect() as conn:
        dataset_max_date = conn.execute(
            text(
                "SELECT MAX(dataset_max_date) FROM deployed_models WHERE status = 'active'"
            )
        ).scalar()

    if isinstance(dataset_max_date, datetime):
        return dataset_max_date.astimezone(timezone.utc)
    else:
        return None
