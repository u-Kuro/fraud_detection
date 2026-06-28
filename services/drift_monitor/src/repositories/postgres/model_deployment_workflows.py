from typing import Optional

from pyarrow.lib import UUID
from sqlalchemy import text

from services.drift_monitor.src.repositories.postgres import engine
from shared.modules.configs import postgres_config

def get_current_model_deployment_workflow() -> Optional[dict]:
    with engine.connect() as connection:
        row = connection.execute(text("""
            SELECT * FROM model_deployment_workflows
                WHERE project_id = :project_id
            LIMIT 1
        """), {
            "project_id": postgres_config.PROJECT_ID
        }).mappings().fetchone()
    return dict(row) if row else None

def create_train_pending_workflow(workflow_id: UUID, drift_slack_ts: str):
    with engine.connect() as connection:
        connection.execute(text("""
            INSERT INTO model_deployment_workflows (
                id,
                project_id,
                state,
                training_approved,
                drift_slack_ts
            )
            VALUES (
               :id, 
               :project_id, 
               'train_pending',
               false,
               :drift_slack_ts
           )
        """),{
            "id": workflow_id,
            "project_id": postgres_config.PROJECT_ID,
            "drift_slack_ts": drift_slack_ts
        })
        connection.commit()

def update_drift_slack_ts(drift_slack_ts: str) -> None:
    with engine.connect() as connection:
        connection.execute(text("""
            UPDATE model_deployment_workflows
            SET drift_slack_ts = :drift_slack_ts
        """),{
            "drift_slack_ts": drift_slack_ts
        })
        connection.commit()

def delete_state() -> None:
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM model_deployment_workflows"))
        connection.commit()

# def update_state_after_training(
#     run_id: str,
#     model_version: int,
#     dataset_min_date: datetime,
#     dataset_max_date: datetime,
# ) -> None:
#     with engine.connect() as conn:
#         conn.execute(text("""
#             UPDATE model_deployment_workflows
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