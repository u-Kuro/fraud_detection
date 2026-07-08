from datetime import datetime, timedelta

from airflow.sdk import dag

from dags.controllers.slack import post_cold_start_training_approval
from dags.modules.configs.dags import dags_config
from dags.repositories.postgres.model_deployment_workflows import create_train_pending_workflow, \
    has_no_ongoing_model_deployment_workflow, has_expired_promote_pending_workflow_with_replacement
from dags.repositories.postgres.model_deployments import has_any_active_model
from dags.services.airflow_operators import no_action
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
    # TODO - finish this
    has_any_active_model() >> [
        has_expired_promote_pending_workflow_with_replacement() >> [
            replace_expired_promote_pending_with_replacement(),
            # replace_challenger_model
            # >> delete_expired_registered_model
            # >> delete_expired_mlflow_run,
            no_action()
        ]
        >> check_for_drift >> [ # kube inside a branch
            check_current_model_deployment_workflow >> [
                post_training_approval,
                update_training_approval,
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
    run_drift_monitor

drift_monitor_dag()