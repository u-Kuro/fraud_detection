from datetime import datetime

from airflow.sdk import dag

from dags.model_lifecycle_orchestrator.check_training_need.modules.configs.airflow.task_ids import DispatchTrainingApprovalTaskIDs, NoActionTaskIDs
from dags.model_lifecycle_orchestrator.check_training_need.repositories.postgres.model_deployments import has_active_model_deployment, get_active_model_deployment
from dags.model_lifecycle_orchestrator.check_training_need.services.tasks import invalidate_expired_challenger_model, drift_check, has_drift, dispatch_training_approval, no_action
from dags.shared.modules.configs.project import ProjectConfig
from dags.shared.services.slack import slack_failure_alert

@dag(
    schedule="@daily",
    start_date=datetime(2026, 1, 1),
    max_active_runs=1,
    catchup=False,
    default_args={
        "on_failure_callback": slack_failure_alert
    },
    is_paused_upon_creation=False,
    tags=[ProjectConfig.project_name, "scheduled", "daily", "monitor", "drift"],
)
def check_training_need():
    active_model_deployment = get_active_model_deployment()
    drift_result = drift_check(active_model_deployment)

    # noinspection unsupported-operator,unresolved-references
    invalidate_expired_challenger_model() \
    >> has_active_model_deployment(active_model_deployment) >> [
        drift_check(active_model_deployment)
        >> has_drift(drift_result) >> [
            dispatch_training_approval(
                task_id=DispatchTrainingApprovalTaskIDs.drifted,
                drift_result=drift_result,
            ),
            no_action(task_id=NoActionTaskIDs.no_drift)
        ],
        dispatch_training_approval(task_id=DispatchTrainingApprovalTaskIDs.cold_start)
    ]

check_training_need()