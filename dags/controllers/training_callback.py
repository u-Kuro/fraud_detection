from datetime import datetime, timedelta

from airflow.sdk import dag

from dags.services.airflow_operators import no_action
from dags.services.training_callback import training_callback, start_training_pipeline

@dag(
    dag_id="training_callback",
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
    tags=["mle", "training", "callback"]
)
def training_callback_dag():
    training_callback() >> [start_training_pipeline(), no_action()]

training_callback_dag()