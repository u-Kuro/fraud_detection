from airflow.sdk import task, get_current_context

from dags.model_lifecycle_orchestrator.on_promotion_decision.modules.schemas.airflow.configurations import PromotionDecisionCallbackConfigurations
from dags.shared.modules.configs.postgres import PostgresConfig
from dags.shared.modules.schemas.postgres.model_deployment_workflows import ModelDeploymentWorkflowsColumnKeys
from dags.shared.modules.schemas.postgres.postgres import PostgresTableKeys
from dags.shared.repositories.postgres import postgres_hook

@task.branch(task_id="update_approved_promotion_workflow")
def update_approved_promotion_workflow() -> None:
    context = get_current_context()

    promotion_decision_callback_configurations = PromotionDecisionCallbackConfigurations.from_context(context)

    postgres_hook.run(f"""
        UPDATE {PostgresTableKeys.model_deployment_workflows}
        SET {ModelDeploymentWorkflowsColumnKeys.promotion_approved} = %({ModelDeploymentWorkflowsColumnKeys.promotion_approved})s
        WHERE 
            {ModelDeploymentWorkflowsColumnKeys.id} = %({ModelDeploymentWorkflowsColumnKeys.id})s
        AND {ModelDeploymentWorkflowsColumnKeys.project_id} = %({ModelDeploymentWorkflowsColumnKeys.project_id})s
        """, parameters={
            ModelDeploymentWorkflowsColumnKeys.id: promotion_decision_callback_configurations.workflow_id,
            ModelDeploymentWorkflowsColumnKeys.project_id: PostgresConfig.PROJECT_ID(),
            ModelDeploymentWorkflowsColumnKeys.promotion_approved: True
        }
    )

@task.branch(task_id="delete_rejected_promotion_workflow")
def delete_rejected_promotion_workflow() -> None:
    context = get_current_context()

    promotion_decision_callback_configurations = PromotionDecisionCallbackConfigurations.from_context(context)

    postgres_hook.run(f"""
        DELETE FROM {PostgresTableKeys.model_deployment_workflows}
        WHERE 
            {ModelDeploymentWorkflowsColumnKeys.id} = %({ModelDeploymentWorkflowsColumnKeys.id})s
        AND {ModelDeploymentWorkflowsColumnKeys.project_id} = %({ModelDeploymentWorkflowsColumnKeys.project_id})s
        """, parameters={
            ModelDeploymentWorkflowsColumnKeys.id: promotion_decision_callback_configurations.workflow_id,
            ModelDeploymentWorkflowsColumnKeys.project_id: PostgresConfig.PROJECT_ID()
        }
    )