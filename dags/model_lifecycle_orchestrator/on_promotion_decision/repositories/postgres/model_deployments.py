from airflow.sdk import task
from sqlalchemy import select, update, insert, true

from dags.model_lifecycle_orchestrator.on_promotion_decision.modules.schemas.airflow.tasks import PromotionDecision, PromotedModelDeployment
from dags.shared.modules.schemas.postgres.model_deployment_workflows import ModelDeploymentWorkflows
from dags.shared.modules.schemas.postgres.model_deployments import ModelDeployments
from dags.shared.repositories.postgres.postgres import sql_session

@task
def promote_model_deployment(promotion_decision_configuration: PromotionDecision) -> PromotedModelDeployment:
    with sql_session.begin() as session:
        project_id_subquery = (
            select(ModelDeploymentWorkflows.project_id)
            .where(ModelDeploymentWorkflows.id == promotion_decision_configuration.model_deployment_workflow.id)
            .limit(1)
            .scalar_subquery()
        )
        session.execute(
            update(ModelDeployments)
            .where(
                ModelDeployments.project_id == project_id_subquery,
                ModelDeployments.active.is_(True)
            )
            .values({
                ModelDeployments.active.key: False
            })
        )

        (dataset_max_timestamp,) = session.execute(
            insert(ModelDeployments)
            .from_select(
                (
                    ModelDeployments.project_id,
                    ModelDeployments.name,
                    ModelDeployments.version,
                    ModelDeployments.mlflow_run_id,
                    ModelDeployments.dataset_min_timestamp,
                    ModelDeployments.dataset_max_timestamp,
                    ModelDeployments.active
                ),
                select(
                    ModelDeploymentWorkflows.project_id,
                    ModelDeploymentWorkflows.registered_model_name,
                    ModelDeploymentWorkflows.registered_model_version,
                    ModelDeploymentWorkflows.mlflow_run_id,
                    ModelDeploymentWorkflows.model_dataset_min_timestamp,
                    ModelDeploymentWorkflows.model_dataset_max_timestamp,
                    true()
                )
                .where(
                    ModelDeploymentWorkflows.id == promotion_decision_configuration.model_deployment_workflow.id
                )
            )
            .returning(
                ModelDeployments.dataset_max_timestamp
            )
        ).one().t

    return PromotedModelDeployment(
        dataset_max_timestamp=dataset_max_timestamp
    )