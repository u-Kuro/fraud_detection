"""
Triggered by fraud_api proxy when a user clicks approve/dismiss on the drift Slack message.
Sets training_approved = true OR deletes pipeline_state.
"""
from datetime import datetime, timedelta

from airflow.sdk import dag, task

@dag(
    dag_id="drift_approval_callback",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args={
        "owner": "mle",
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
        "email_on_failure": False
    },
    tags=["mle", "callback"]
)
def drift_approval_callback_dag():

    @task
    def handle_action(dag_run=None):
        from sqlalchemy import create_engine, text

        conf = dag_run.conf or {}
        action = conf.get("action")
        engine = create_engine("postgresql+psycopg2://", pool_pre_ping=True)
        try:
            if action == "approved":
                with engine.begin() as connection:
                    connection.execute(text("""
                        UPDATE pipeline_state
                        SET training_approved = true
                        WHERE state = 'drift_pending'
                    """))
            elif action == "dismissed":
                with engine.begin() as connection:
                    connection.execute(text("DELETE FROM pipeline_state"))
            else:
                raise ValueError(f"Unknown action: {action!r}")
        finally:
            engine.dispose()

    handle_action()

drift_approval_callback_dag()