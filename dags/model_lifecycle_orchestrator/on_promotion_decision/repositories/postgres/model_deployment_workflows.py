from airflow.sdk import task, get_current_context
from sqlalchemy import update, delete

from dags.model_lifecycle_orchestrator.on_promotion_decision.modules.schemas.airflow.configurations import PromotionDecisionCallbackConfigurations
from dags.shared.modules.configs.postgres import PostgresConfig
from dags.shared.modules.schemas.postgres.model_deployment_workflows import ModelDeploymentWorkflows
from dags.shared.repositories.postgres.postgres import sql_session

@task.branch(task_id="update_approved_promotion_workflow")
def update_approved_promotion_workflow() -> None:
    context = get_current_context()

    promotion_decision_callback_configurations = PromotionDecisionCallbackConfigurations.from_context(context)

    with sql_session.begin() as session:
        session.execute(
            update(ModelDeploymentWorkflows)
            .where(
                ModelDeploymentWorkflows.id == promotion_decision_callback_configurations.workflow_id,
                ModelDeploymentWorkflows.project_id == PostgresConfig.project_id()
            )
            .values({
                ModelDeploymentWorkflows.promotion_approved.key: True
            })
        )

@task.branch(task_id="delete_rejected_promotion_workflow")
def delete_rejected_promotion_workflow() -> None:
    context = get_current_context()

    promotion_decision_callback_configurations = PromotionDecisionCallbackConfigurations.from_context(context)

    with sql_session.begin() as session:
        session.execute(
            delete(ModelDeploymentWorkflows)
            .where(
                ModelDeploymentWorkflows.id == promotion_decision_callback_configurations.workflow_id,
                ModelDeploymentWorkflows.project_id == PostgresConfig.project_id()
            )
        )