from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.engine import Engine

def get_archive_cutoff(engine: Engine) -> datetime | None:
    """
    Returns the highest dataset_max_date across all ACTIVE model_deployments.
    Data at or before this timestamp is safe to archive.
    Returns None if no active model exists.
    """
    with engine.connect() as conn:
        dataset_max_date = conn.execute(
            text(
                "SELECT MAX(dataset_max_date) FROM model_deployments WHERE status = 'active'"
            )
        ).scalar()

    if isinstance(dataset_max_date, datetime):
        return dataset_max_date.astimezone(timezone.utc)
    else:
        return None
