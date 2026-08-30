from airflow.sdk import task, TriggerRule
from sqlalchemy import select

from dags.model_lifecycle_orchestrator.check_training_need.modules.configs.airflow.task_ids import DispatchTrainingApprovalTaskIDs
from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.airflow.tasks import  ActiveModelDeployment
from dags.model_lifecycle_orchestrator.check_training_need.services.tasks import drift_check
from dags.shared.modules.configs.postgres import PostgresConfig
from dags.shared.modules.schemas.postgres.model_deployments import ModelDeployments
from dags.shared.repositories.postgres.postgres import sql_session

@task
def get_active_model_deployment() -> ActiveModelDeployment | None:
    with sql_session.begin() as session:
        mlflow_run_id = session.execute(
            select(ModelDeployments.mlflow_run_id)
            .where(
                ModelDeployments.project_id == PostgresConfig.project_id(),
                ModelDeployments.active.is_(True)
            )
            .limit(1)
        ).scalar_one_or_none()

    if mlflow_run_id is None:
        return None
    else:
        return ActiveModelDeployment(
            mlflow_run_id=mlflow_run_id
        )

@task.branch(trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)
def has_active_model_deployment(
    active_model_deployment: ActiveModelDeployment | None
) -> str:
    if active_model_deployment is None:
        return DispatchTrainingApprovalTaskIDs.cold_start
    else:
        return drift_check.__name__