from datetime import datetime, timedelta

from airflow.sdk import dag

from dags.shared.services.airflow_operators import no_action
from dags.model_lifecycle_orchestrator.sub_dags.promotion_callback.services.promotion_callback import promotion_callback, start_promotion_pipeline

@dag(
    dag_id="promotion_callback",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    max_active_runs=1,
    catchup=True,
    default_args={
        "owner": "mle",
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
        "email_on_failure": False
    },
    tags=["mle", "promotion", "callback"]
)
def promotion_callback_dag():
    promotion_callback() >> [start_promotion_pipeline(), no_action()]

promotion_callback_dag()