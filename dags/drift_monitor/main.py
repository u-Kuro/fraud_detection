from datetime import datetime, timedelta

from airflow.sdk import dag

from dags.drift_monitor.controllers.slack import post_retraining_approval, update_retraining_approval, post_cold_start_training_approval
from dags.drift_monitor.repositories.mlflow.registered_model import replace_expired_model, delete_expired_model
from dags.drift_monitor.repositories.mlflow.run import delete_expired_mlflow_run
from dags.drift_monitor.repositories.postgres.model_deployment_workflows import create_train_pending_workflow, has_no_ongoing_model_deployment_workflow, has_expired_promote_pending_workflow_with_replacement, check_current_model_deployment_workflow, update_training_pending_workflow
from dags.drift_monitor.repositories.postgres.model_deployments import has_any_active_model
from dags.drift_monitor.services.tasks import drift_check, has_drift

from dags.shared.modules.configs import airflow_config
from dags.shared.services.airflow_operators import no_action

@dag(
    dag_id="drift_monitor",
    schedule="0 */6 * * *",
    start_date=datetime(2026, 1, 1),
    max_active_runs=1,
    catchup=True,
    default_args={
        "owner": airflow_config.OWNER,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "email_on_failure": False
    },
    tags=["mle", "drift"]
)
def drift_monitor_dag():
    has_any_active_model() >> [
        has_expired_promote_pending_workflow_with_replacement() >> [
            replace_expired_model()
            >> delete_expired_model()
            >> delete_expired_mlflow_run(),
            no_action()
        ]
        >> drift_check
        >> has_drift() >> [
            check_current_model_deployment_workflow() >> [
                post_retraining_approval()
                >> create_train_pending_workflow(),
                update_retraining_approval()
                >> update_training_pending_workflow(),
                no_action()
            ],
            no_action()
        ],
        has_no_ongoing_model_deployment_workflow() >> [
            post_cold_start_training_approval()
            >> create_train_pending_workflow(),
            no_action()
        ]
    ]

drift_monitor_dag()