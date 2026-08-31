from airflow.sdk import task
from sqlalchemy import update, delete

from dags.model_lifecycle_orchestrator.on_promotion_decision.modules.schemas.airflow.tasks import PromotionDecision
from dags.shared.modules.configs.postgres import PostgresConfig
from dags.shared.modules.schemas.postgres.model_deployment_workflows import ModelDeploymentWorkflows
from dags.shared.repositories.postgres.postgres import sql_session

@task
def update_approved_promotion_workflow(promotion_decision: PromotionDecision):
    with sql_session.begin() as session:
        session.execute(
            update(ModelDeploymentWorkflows)
            .where(
                ModelDeploymentWorkflows.id == promotion_decision.model_deployment_workflow.id,
                ModelDeploymentWorkflows.project_id == PostgresConfig.project_id()
            )
            .values({
                ModelDeploymentWorkflows.promotion_approved.key: True
            })
        )

@task
def delete_rejected_promotion_workflow(data: PromotionDecision):
    with sql_session.begin() as session:
        session.execute(
            delete(ModelDeploymentWorkflows)
            .where(
                ModelDeploymentWorkflows.id == data.model_deployment_workflow,
                ModelDeploymentWorkflows.project_id == PostgresConfig.project_id()
            )
        )