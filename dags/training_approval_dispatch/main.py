from datetime import datetime, timedelta

from airflow.sdk import dag

from dags.model_lifecycle_orchestrator.controllers.slack import post_training_approval, update_training_approval, post_cold_start_training_approval
from dags.model_lifecycle_orchestrator.repositories.postgres.model_deployment_workflows import create_train_pending_workflow, check_current_model_deployment_workflow, update_training_pending_workflow

from dags.shared.modules.configs import airflow_config
from dags.shared.modules.configs.airflow.airflow import DagIDs, AirflowConfig
from dags.shared.services.airflow_operators import no_action

@dag(
    dag_id=DagIDs.training_approval_dispatch,
    schedule="0 */6 * * *",
    start_date=datetime(2026, 1, 1),
    max_active_runs=1,
    catchup=True,
    default_args={
        "owner": AirflowConfig.owner,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "email_on_failure": False
    },
    tags=["mle", "training", "approval", "dispatch"]
)
def training_approval_dispatch():


training_approval_dispatch()