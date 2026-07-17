from airflow.sdk import task

from dags.model_lifecycle_monitor.repositories.postgres.model_deployment_workflows import has_no_ongoing_model_deployment_workflow, has_expired_promote_pending_workflow_with_replacement

from dags.shared.modules.configs.postgres import postgres_config
from dags.shared.repositories.postgres import postgres_hook

@task.branch(task_id="has_any_active_model")
def has_any_active_model() -> str:
    result = postgres_hook.get_first("""
        SELECT EXISTS (
            SELECT 1 FROM model_deployments
            WHERE
                project_id = %(project_id)s
            AND active
        )
        """, {
            "project_id": postgres_config.PROJECT_ID
        }
    )
    has_active_model = bool(result[0])

    if has_active_model:
        return has_expired_promote_pending_workflow_with_replacement.__name__
    else:
        return has_no_ongoing_model_deployment_workflow.__name__