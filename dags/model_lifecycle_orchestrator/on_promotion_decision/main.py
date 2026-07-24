from datetime import datetime, timedelta

from airflow.sdk import dag

from dags.shared.modules.configs.airflow.airflow import DagIDs, AirflowConfig

@dag(
    dag_id=DagIDs.on_promotion_decision,
    schedule=None,
    start_date=datetime(2026, 1, 1),
    max_active_runs=1,
    catchup=True,
    default_args={
        "owner": AirflowConfig.owner,
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
        "email_on_failure": False
    },
    tags=["mle", "triggered", "promotion", "decision"]
)
def on_promotion_decision():
    # TODO - 24/07/2026 - Continue here...
    promotion_decision_callback() >> [
        update_approved_promotion_workflow() \
        # add model deployment
        # switch mlflow registered model alias
        # update model deployment to active

        delete_rejected_promotion_workflow()
    ]

on_promotion_decision()