from datetime import datetime, timedelta

from airflow.sdk import dag

from dags.modules.configs.dags import dags_config
from dags.services.drift_monitor import run_drift_monitor

@dag(
    dag_id="drift_monitor",
    schedule="0 */6 * * *",
    start_date=datetime(2026, 1, 1),
    max_active_runs=1,
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
    # if postgres - has_any_active_model?
        # if postgres - has_expired_promote_pending_workflow_with_replacement?
            # 1. mlflow - put challenger alias from expired to replacement
            # 2. mlflow - delete expired registered model
            # 3. mlflow - delete expired run
        # kube pod - check for drift
        # if xcom - drift detected
            # postgres - get current workflow
            # if no current workflow
                # slack - post training approval
            # elif workflow state is train_pending
                # slack - update training approval
    # elif postgres - has_no_ongoing_model_deployment_workflow?
        # 1. slack - post_message
        # 2. postgres - update workflow
    run_drift_monitor

drift_monitor_dag()