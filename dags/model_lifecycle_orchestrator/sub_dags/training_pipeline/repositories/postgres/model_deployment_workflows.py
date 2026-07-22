from datetime import datetime

from airflow.sdk import task

from dags.shared.modules.configs import postgres_config
from dags.shared.modules.schemas.postgres.model_deployment_workflows import ModelDeploymentWorkflowState
from dags.shared.repositories.postgres import postgres_hook
from dags.shared.services.airflow_operators import no_action
from dags.model_lifecycle_orchestrator.sub_dags.training_pipeline.modules.schemas.airflow.xcom import UpdateDeploymentWorkflowXCom

@task(task_id="update_deployment_workflow")
def update_deployment_workflow(**context) -> str:
    update_deployment_workflow_xcom = UpdateDeploymentWorkflowXCom.from_context(context)

    postgres_hook.run("""
        UPDATE model_deployment_workflows
        SET model_trained_at = %(model_trained_at)s,
            mlflow_run_id = %(mlflow_run_id)s,
            registered_model_name = %(registered_model_name)s,
            registered_model_version = %(registered_model_version)s,
            model_dataset_min_timestamp = %(model_dataset_min_timestamp)s,
            model_dataset_max_timestamp = %(model_dataset_max_timestamp)s
        WHERE id = %(id)s
        """, parameters={
            "id": update_deployment_workflow_xcom.workflow_id,
            "model_trained_at": datetime.fromisoformat(update_deployment_workflow_xcom.model_trained_at_iso_datetime),
            "mlflow_run_id": update_deployment_workflow_xcom.mlflow_run_id,
            "registered_model_name": update_deployment_workflow_xcom.model_name,
            "registered_model_version": update_deployment_workflow_xcom.model_version,
            "model_dataset_min_timestamp": datetime.fromisoformat(update_deployment_workflow_xcom.model_dataset_min_iso_datetime),
            "model_dataset_max_timestamp": datetime.fromisoformat(update_deployment_workflow_xcom.model_dataset_max_iso_datetime),
        }
    )

    return has_no_primary_model_deployment_workflow.__name__

@task.branch(task_id="has_no_primary_model_deployment_workflow")
def has_no_primary_model_deployment_workflow() -> str:
    result = postgres_hook.get_first("""
        SELECT EXISTS (
            SELECT 1 FROM model_deployment_workflows
            WHERE
                project_id = %(project_id)s
            AND state = %(promote_pending_state)s
        )
        """, {
        "project_id": postgres_config.PROJECT_ID,
        "promote_pending_state": ModelDeploymentWorkflowState.promote_pending
    }
                                     )
    has_primary_model_deployment_workflow = bool(result[0])

    if has_primary_model_deployment_workflow:
        return no_action.__name__
    else:
        return post_slack_promotion_approval.__name__