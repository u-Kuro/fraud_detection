"""All pipeline_state + deployed_models mutations used during training + promotion."""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import text
from sqlalchemy.engine import Engine


def get_latest_deployed_max_date(engine: Engine) -> datetime:
    """Lower bound for training data — use data strictly after this timestamp."""
    with engine.connect() as conn:
        val = conn.execute(
            text(
                "SELECT MAX(dataset_max_date) FROM deployed_models WHERE status = 'active'"
            )
        ).scalar()
    return (
        val.astimezone(timezone.utc)
        if val
        else datetime(1970, 1, 1, tzinfo=timezone.utc)
    )


def get_current_state(engine: Engine) -> Optional[dict]:
    with engine.connect() as conn:
        row = (
            conn.execute(text("SELECT * FROM pipeline_state LIMIT 1"))
            .mappings()
            .fetchone()
        )
    return dict(row) if row else None


def update_after_training(
    engine: Engine,
    run_id: str,
    model_version: int,
    dataset_min_date: datetime,
    dataset_max_date: datetime,
) -> None:
    with engine.connect() as conn:
        conn.execute(
            text("""
            UPDATE pipeline_state
            SET state = 'train_pending',
                run_id = :run_id,
                model_version = :mv,
                dataset_min_date = :dmin,
                dataset_max_date = :dmax
        """),
            {
                "run_id": run_id,
                "mv": model_version,
                "dmin": dataset_min_date,
                "dmax": dataset_max_date,
            },
        )
        conn.commit()


def begin_promoting(
    engine: Engine,
    run_id: str,
    model_name: str,
    model_version: int,
    dataset_min_date: datetime,
    dataset_max_date: datetime,
) -> None:
    """Atomically create the intent record and set state = promoting."""
    with engine.connect() as conn:
        conn.execute(
            text("""
            INSERT INTO deployed_models (model_name, model_version, dataset_min_date, dataset_max_date, status, promoted_at)
            VALUES (:name, :mv, :dmin, :dmax, 'promoting', NOW())
            ON CONFLICT (model_name, model_version) DO UPDATE SET status = 'promoting'
        """),
            {
                "name": model_name,
                "mv": model_version,
                "dmin": dataset_min_date,
                "dmax": dataset_max_date,
            },
        )
        conn.execute(text("UPDATE pipeline_state SET state = 'promoting'"))
        conn.commit()


def finalize_promotion(engine: Engine, model_name: str, model_version: int) -> None:
    """Atomically set deployed_model active and delete pipeline_state."""
    with engine.connect() as conn:
        conn.execute(
            text("""
            UPDATE deployed_models SET status = 'active'
            WHERE model_name = :name AND model_version = :mv
        """),
            {"name": model_name, "mv": model_version},
        )
        conn.execute(text("DELETE FROM pipeline_state"))
        conn.commit()
