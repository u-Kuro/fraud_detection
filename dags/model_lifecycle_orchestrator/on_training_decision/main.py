from datetime import datetime, timedelta

from airflow.sdk import dag

from dags.model_lifecycle_orchestrator.on_training_decision.controllers.slack import initialize_promotion_approval, update_promotion_approval
from dags.model_lifecycle_orchestrator.on_training_decision.repositories.postgres.model_deployment_workflows import update_approved_training_workflow, delete_rejected_training_workflow, update_trained_model_info_in_workflow, update_promotion_pending_workflow
from dags.model_lifecycle_orchestrator.on_training_decision.services.tasks import training_decision_callback, train_model
from dags.shared.modules.configs.airflow.airflow import DagIDs, AirflowConfig

@dag(
    dag_id=DagIDs.on_training_decision,
    schedule=None,
    start_date=datetime(2026, 1, 1),
    is_paused_upon_creation=False,
    max_active_runs=1,
    default_args={
        "owner": AirflowConfig.owner,
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
        "email_on_failure": False
    },
    tags=["mle", "triggered", "training", "decision"]
)
def on_training_decision():
    training_decision_callback() >> [
        update_approved_training_workflow() \
        >> train_model() \
        >> update_trained_model_info_in_workflow() \
        >> initialize_promotion_approval() \
        >> update_promotion_pending_workflow() \
        >> update_promotion_approval(),

        delete_rejected_training_workflow()
    ]

on_training_decision()