from airflow.sdk import task, TriggerRule

from dags.shared.modules.configs.postgres import PostgresConfig
from dags.shared.repositories.postgres import postgres_hook
from dags.training_approval_dispatch.services.tasks import drift_check_task_id

@task.branch(
    task_id="has_any_active_model",
    trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS
)
def has_any_active_model() -> str:
    result = postgres_hook.get_first("""
        SELECT EXISTS (
            SELECT 1 FROM model_deployments
            WHERE
                project_id = %(project_id)s
            AND active
        )
        """, {
            "project_id": PostgresConfig.PROJECT_ID
        }
    )
    has_active_model = bool(result[0])

    if has_active_model:
        return drift_check_task_id
    else:
        return f"{dispatch_training_approval.__name__}.{check_current_model_deployment_workflow.__name__}"