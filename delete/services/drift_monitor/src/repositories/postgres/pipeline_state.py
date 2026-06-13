import logging
from datetime import datetime
from typing import Optional
from sqlalchemy import text

from services.drift_monitor.src.repositories.postgres import engine

def get_pipeline_state() -> Optional[dict]:
    with engine.connect() as connection:
        row = connection.execute(text(
            "SELECT * FROM pipeline_state LIMIT 1"
        )).mappings().fetchone()
    return dict(row) if row else None

def create_drift_pending(slack_message_id: str) -> None:
    with engine.connect() as connection:
        connection.execute(text("""
            INSERT INTO pipeline_state (
                state,
                drift_approved,
                slack_message_id
            )
            VALUES (
               'drift_pending',
               false,
               :slack_message_id
           )
        """),{
            "slack_message_id": slack_message_id
        })
        connection.commit()

def update_drift_message_id(slack_message_id: str) -> None:
    with engine.connect() as connection:
        connection.execute(text("""
            UPDATE pipeline_state
            SET slack_message_id = :slack_message_id
        """),{
            "slack_message_id": slack_message_id
        })
        connection.commit()

def delete_state() -> None:
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM pipeline_state"))
        conn.commit()

def update_state_after_training(
    run_id: str,
    model_version: int,
    dataset_min_date: datetime,
    dataset_max_date: datetime,
) -> None:
    with engine.connect() as conn:
        conn.execute(text("""
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
        conn.commit()