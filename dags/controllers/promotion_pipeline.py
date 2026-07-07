from datetime import datetime, timedelta

from airflow.sdk import dag

from dags.modules.configs.dags import dags_config
from dags.services.promotion_pipeline import run_promotion

@dag(
    dag_id="promotion_pipeline",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    max_active_runs=1,
    catchup=True,
    default_args={
        "owner": dags_config.OWNER,
        "retries": 1,
        "retry_delay": timedelta(minutes=10),
        "email_on_failure": False
    },
    tags=["mle", "promotion"]
)
def promotion_pipeline_dag():
    run_promotion()