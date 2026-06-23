from typing import Optional
from sqlalchemy import text

from services.drift_monitor.src.repositories.postgres import engine

def get_pipeline_state() -> Optional[dict]:
    with engine.connect() as connection:
        row = connection.execute(text(
            "SELECT * FROM pipeline_state LIMIT 1"
        )).mappings().fetchone()
    return dict(row) if row else None

def create_drift_pending(drift_slack_ts: str) -> None:
    with engine.connect() as connection:
        connection.execute(text("""
            INSERT INTO pipeline_state (
                state,
                training_approved,
                drift_slack_ts
            )
            VALUES (
               'drift_pending',
               false,
               :drift_slack_ts
           )
        """),{
            "drift_slack_ts": drift_slack_ts
        })
        connection.commit()

def update_drift_slack_ts(drift_slack_ts: str) -> None:
    with engine.connect() as connection:
        connection.execute(text("""
            UPDATE pipeline_state
            SET drift_slack_ts = :drift_slack_ts
        """),{
            "drift_slack_ts": drift_slack_ts
        })
        connection.commit()

def delete_state() -> None:
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM pipeline_state"))
        connection.commit()

# def update_state_after_training(
#     run_id: str,
#     model_version: int,
#     dataset_min_date: datetime,
#     dataset_max_date: datetime,
# ) -> None:
#     with engine.connect() as conn:
#         conn.execute(text("""
#             UPDATE pipeline_state
#             SET state = 'train_pending',
#                 run_id = :run_id,
#                 model_version = :model_version,
#                 dataset_min_date = :dataset_min_date,
#                 dataset_max_date = :dataset_max_date
#         """), {
#             "run_id": run_id,
#             "model_version": model_version,
#             "dataset_min_date": dataset_min_date,
#             "dataset_max_date": dataset_max_date,
#         })
#         conn.commit()