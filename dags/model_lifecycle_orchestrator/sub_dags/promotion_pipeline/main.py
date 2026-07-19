from datetime import datetime, timedelta

from airflow.sdk import dag

from dags.shared.modules.configs import airflow_config
from dags.model_lifecycle_orchestrator.sub_dags.promotion_pipeline.services.promotion_pipeline import run_promotion
from dags.shared.modules.configs.airflow.airflow import AirflowConfig


@dag(
    dag_id="promotion_pipeline",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    max_active_runs=1,
    catchup=True,
    default_args={
        "owner": AirflowConfig.owner,
        "retries": 1,
        "retry_delay": timedelta(minutes=10),
        "email_on_failure": False
    },
    tags=["mle", "promotion"]
)
def promotion_pipeline_dag():
    run_promotion()

promotion_pipeline_dag()