from datetime import datetime, timedelta

from airflow.sdk import dag

from dags.model_lifecycle_orchestrator.on_promotion_decision.repositories.postgres.model_deployment_workflows import \
    update_approved_promotion_workflow, delete_rejected_promotion_workflow
from dags.model_lifecycle_orchestrator.on_promotion_decision.repositories.postgres.model_deployments import \
    promote_model_deployment
from dags.model_lifecycle_orchestrator.on_promotion_decision.services.tasks import promotion_decision_callback, \
    apply_model_deployment
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
    promotion_decision_callback() >> [
        update_approved_promotion_workflow() \
        >> promote_model_deployment() \
        >> apply_model_deployment(),

        delete_rejected_promotion_workflow()
    ]

on_promotion_decision()