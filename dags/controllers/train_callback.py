from datetime import datetime, timedelta

from airflow.sdk import dag

from dags.services.train_callback import train_callback

@dag(
    dag_id="train_callback",
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
def train_callback_dag():
    train_callback()

train_callback_dag()