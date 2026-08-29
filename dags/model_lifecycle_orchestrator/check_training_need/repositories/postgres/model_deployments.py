from airflow.sdk import task, TriggerRule, get_current_context
from sqlalchemy import select

from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.airflow.branches import DispatchTrainingApprovalBranches
from dags.model_lifecycle_orchestrator.check_training_need.services.tasks import dispatch_training_approval, drift_check
from dags.shared.modules.configs.airflow.data_keys import ModelDeploymentKeys
from dags.shared.modules.configs.postgres import PostgresConfig
from dags.shared.modules.schemas.airflow import AirflowTaskContext
from dags.shared.modules.schemas.postgres.model_deployments import ModelDeployments
from dags.shared.modules.utilities.airflow.xcom import build_task_id
from dags.shared.repositories.postgres.postgres import sql_session

@task.branch(
    task_id="has_any_active_model",
    trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS
)
def has_any_active_model() -> str:
    with sql_session.begin() as session:
        mlflow_run_id = session.execute(
            select(ModelDeployments.mlflow_run_id)
            .where(
                ModelDeployments.project_id == PostgresConfig.project_id(),
                ModelDeployments.active.is_(True)
            )
            .limit(1)
        ).scalar_one_or_none()

    if mlflow_run_id is not None:
        if not isinstance(mlflow_run_id, str):
            raise ValueError(f"Unexpected mlflow run id type {type(mlflow_run_id)!r}, expecting a string.")
        context = get_current_context()
        ti = AirflowTaskContext.from_context(context).ti
        ti.xcom_push(
            key=ModelDeploymentKeys.MODEL_DEPLOYMENT_MLFLOW_RUN_ID,
            value=mlflow_run_id,
        )
        return drift_check.__name__
    else:
        return build_task_id((
            dispatch_training_approval.__name__,
            DispatchTrainingApprovalBranches.cold_start
        ))