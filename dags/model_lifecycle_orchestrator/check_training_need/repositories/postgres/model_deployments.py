from airflow.sdk import task, TriggerRule

from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.airflow.branches import DispatchTrainingApprovalBranches
from dags.model_lifecycle_orchestrator.check_training_need.repositories.postgres.model_deployment_workflows import check_current_model_deployment_workflows
from dags.model_lifecycle_orchestrator.check_training_need.services.tasks import dispatch_training_approval, drift_check
from dags.shared.modules.configs.postgres import PostgresConfig
from dags.shared.modules.schemas.postgres.model_deployments import ModelDeploymentsColumnKeys
from dags.shared.modules.schemas.postgres.postgres import PostgresTableKeys
from dags.shared.modules.utilities.airflow.xcom import build_task_id
from dags.shared.repositories.postgres import postgres_hook

@task.branch(
    task_id="has_any_active_model",
    trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS
)
def has_any_active_model() -> str:
    result = postgres_hook.get_first(f"""
        SELECT EXISTS (
            SELECT 1
            FROM {PostgresTableKeys.model_deployments}
            WHERE
                {ModelDeploymentsColumnKeys.project_id} = %({ModelDeploymentsColumnKeys.project_id})s
            AND {ModelDeploymentsColumnKeys.active}
        )
        """, {
            ModelDeploymentsColumnKeys.project_id: PostgresConfig.PROJECT_ID()
        }
    )
    has_active_model = bool(result[0])

    if has_active_model:
        return drift_check.__name__
    else:
        return build_task_id((
            dispatch_training_approval.__name__,
            DispatchTrainingApprovalBranches.cold_start,
            check_current_model_deployment_workflows.__name__
        ))