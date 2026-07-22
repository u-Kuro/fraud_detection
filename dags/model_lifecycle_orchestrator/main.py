from datetime import datetime, timedelta

from airflow.sdk import dag

from dags.model_lifecycle_orchestrator.modules.schemas.airflow.branches import DispatchTrainingApprovalBranches, NoActionBranches
from dags.model_lifecycle_orchestrator.repositories.postgres.model_deployments import has_any_active_model
from dags.model_lifecycle_orchestrator.services.tasks import invalidate_expired_challenger_model, drift_check, has_drift, dispatch_training_approval, no_action
from dags.shared.modules.configs.airflow.airflow import DagIDs, AirflowConfig

@dag(
    dag_id=DagIDs.model_lifecycle_orchestrator,
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
    tags=["mle", "model", "lifecycle", "monitor"]
)
def model_lifecycle_monitor():
    invalidate_expired_challenger_model() \
    >> has_any_active_model() >> [
        drift_check \
        >> has_drift() >> [
            dispatch_training_approval(branch=DispatchTrainingApprovalBranches.drifted),
            no_action(branch=NoActionBranches.no_drift)
        ],
        dispatch_training_approval(branch=DispatchTrainingApprovalBranches.cold_start)
    ]

model_lifecycle_monitor()