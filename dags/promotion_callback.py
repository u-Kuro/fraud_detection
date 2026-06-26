"""
Triggered by fraud_api proxy when a user clicks approve/reject on the promotion Slack message.
Sets promote_approved = true OR rejects and cleans up MLflow candidate.
"""
import os
from datetime import datetime, timedelta

from airflow.sdk import dag, task

@dag(
    dag_id="promotion_callback",
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
def promotion_callback_dag():
    @task
    def handle_action(dag_run=None):
        from sqlalchemy import create_engine, text

        conf = dag_run.conf or {}
        action = conf.get("action")
        engine = create_engine("postgresql+psycopg2://", pool_pre_ping=True)
        try:
            if action == "approved":
                with engine.begin() as conn:
                    conn.execute(text("""
                        UPDATE pipeline_state
                        SET promote_approved = true
                        WHERE state = 'train_pending'
                    """))
            elif action == "rejected":
                with engine.connect() as conn:
                    row = conn.execute(text("""
                        SELECT run_id
                        FROM pipeline_state
                        WHERE state = 'train_pending'
                        LIMIT 1
                    """)).mappings().fetchone()
                with engine.begin() as conn:
                    conn.execute(text("DELETE FROM pipeline_state"))
                if row: cleanup_mlflow(row["run_id"])
            else: raise ValueError(f"Unknown action: {action!r}")
        finally:
            engine.dispose()

    handle_action()


def cleanup_mlflow(run_id: str) -> None:
    import mlflow
    from mlflow import MlflowClient

    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "http://mlflow:5000")
    production = os.environ.get("MLFLOW_PRODUCTION_ALIAS", "production")
    mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient()
    try:
        for v in client.search_model_versions(f"run_id='{run_id}'"):
            aliases = getattr(v, "aliases", []) or []
            for alias in aliases:
                if alias != production:
                    try: client.delete_registered_model_alias(v.name, alias)
                    except: pass
            if production not in aliases:
                try: client.delete_model_version(v.name, str(v.version))
                except: pass
    except Exception as exception:
        import logging
        logging.getLogger(__name__).warning(f"MLflow cleanup failed (non-fatal): {exception}")


promotion_callback_dag()