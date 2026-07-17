from datetime import datetime, timedelta

from airflow.sdk import dag

from dags.challenger_model_rotation.repositories.mlflow.registered_model import replace_expired_model, delete_expired_model
from dags.challenger_model_rotation.repositories.mlflow.run import delete_expired_mlflow_run
from dags.challenger_model_rotation.repositories.postgres.model_deployment_workflows import has_expired_promote_pending_workflow_with_replacement

from dags.shared.modules.configs import airflow_config
from dags.shared.modules.configs.airflow.airflow import DagIDs
from dags.shared.services.airflow_operators import no_action

@dag(
    dag_id=DagIDs.CHALLENGER_MODEL_ROTATION,
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
    tags=["mle", "challenger", "rotation", "cleanup"]
)
def challenger_model_rotation():
    has_expired_promote_pending_workflow_with_replacement() >> [
        replace_expired_model()
        >> delete_expired_model()
        >> delete_expired_mlflow_run(),
        no_action()
    ]

challenger_model_rotation()