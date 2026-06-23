"""All pipeline_state + deployed_models mutations used during training + promotion."""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import text

from services.training_pipeline.src.repositories.postgres import engine

def get_latest_deployed_max_date() -> datetime:
    """Lower bound for training data — use data strictly after this timestamp."""
    with engine.connect() as connection:
        dataset_max_date = connection.execute(text("""
            SELECT MAX(dataset_max_date) FROM deployed_models
            WHERE status = 'active'
        """)).scalar()
    return (
        dataset_max_date.astimezone(timezone.utc)
        if dataset_max_date
        else datetime(1970, 1, 1, tzinfo=timezone.utc)
    )

def get_current_state() -> Optional[dict]:
    with engine.connect() as connection:
        row = connection.execute(text("""
            SELECT * FROM pipeline_state
            LIMIT 1
        """)).mappings().fetchone()

    return dict(row) if row else None

def update_after_training(
    run_id: str,
    model_version: int,
    dataset_min_date: datetime,
    dataset_max_date: datetime,
) -> None:
    with engine.connect() as connection:
        connection.execute(text("""
            UPDATE pipeline_state
            SET state = 'train_pending',
                run_id = :run_id,
                model_version = :model_version,
                dataset_min_date = :dataset_min_date,
                dataset_max_date = :dataset_max_date
        """), {
            "run_id": run_id,
            "model_version": model_version,
            "dataset_min_date": dataset_min_date,
            "dataset_max_date": dataset_max_date,
        })
        connection.commit()

def update_promote_slack_ts(promote_slack_ts: str) -> None:
    with engine.connect() as connection:
        connection.execute(text("""
            UPDATE pipeline_state
            SET promote_slack_ts = :promote_slack_ts
        """), {
            "promote_slack_ts": promote_slack_ts
        })
        connection.commit()

def begin_promoting(
    model_name: str,
    model_version: int,
    dataset_min_date: datetime,
    dataset_max_date: datetime,
) -> None:
    """Atomically create the intent record and set state = promoting."""
    with engine.connect() as connection:
        connection.execute(text("""
            INSERT INTO deployed_models (
                model_name,
                model_version,
                dataset_min_date,
                dataset_max_date,
                status
            )
            VALUES (
                :name,
                :model_version,
                :dataset_min_date,
                :dataset_max_date,
                'promoting'
            )
            ON CONFLICT (model_name, model_version)
            DO UPDATE SET status = 'promoting'
        """), {
            "model_name": model_name,
            "model_version": model_version,
            "dataset_min_date": dataset_min_date,
            "dataset_max_date": dataset_max_date,
        })
        connection.execute(text("""
            UPDATE pipeline_state
            SET state = 'promoting'
        """))
        connection.commit()


def finalize_promotion(
    model_name: str,
    model_version: int
) -> None:
    """Atomically set deployed_model active and delete pipeline_state."""
    with engine.connect() as connection:
        connection.execute(text("""
            UPDATE deployed_models
            SET status = 'active'
            WHERE model_name = :model_name AND model_version = :model_version
        """), {
            "model_name": model_name,
            "model_version": model_version
        })
        connection.execute(text("""
            DELETE FROM pipeline_state
        """))
        connection.commit()
