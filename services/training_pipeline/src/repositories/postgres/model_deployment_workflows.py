"""All model_deployment_workflows + model_deployments mutations used during training + promotion."""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import text

from services.training_pipeline.src.repositories.postgres import engine

def get_latest_deployed_max_date() -> datetime:
    with engine.connect() as connection:
        dataset_max_date = connection.execute(text("""
            SELECT MAX(dataset_max_date) FROM model_deployments
            WHERE status = 'active'
        """)).scalar()

    if isinstance(dataset_max_date, datetime):
        return dataset_max_date.astimezone(timezone.utc)
    else:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)

def get_current_state() -> Optional[dict]:
    with engine.connect() as connection:
        row = connection.execute(text("""
            SELECT * FROM model_deployment_workflows
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
            UPDATE model_deployment_workflows
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
            UPDATE model_deployment_workflows
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
    with engine.connect() as connection:
        connection.execute(text("""
            INSERT INTO model_deployments (
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
            UPDATE model_deployment_workflows
            SET state = 'promoting'
        """))
        connection.commit()


def finalize_promotion(
    model_name: str,
    model_version: int
) -> None:
    with engine.connect() as connection:
        connection.execute(text("""
            UPDATE model_deployments
            SET status = 'active'
            WHERE   model_name = :model_name
                AND model_version = :model_version
        """), {
            "model_name": model_name,
            "model_version": model_version
        })
        connection.execute(text("""
            DELETE FROM model_deployment_workflows
        """))
        connection.commit()
