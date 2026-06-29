from datetime import datetime, timedelta

from airflow.sdk import dag

from dags.modules.configs.dags import dags_config
from dags.services.drift_monitor import run_drift_monitor

@dag(
    dag_id="drift_monitor",
    max_active_runs=1,
    schedule="0 */6 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=True,
    default_args={
        "owner": dags_config.OWNER,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "email_on_failure": False
    },
    tags=["mle", "drift"]
)
def drift_monitor_dag():
    run_drift_monitor

drift_monitor_dag()