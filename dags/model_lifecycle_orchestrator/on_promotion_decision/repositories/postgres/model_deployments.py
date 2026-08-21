from airflow.sdk import task, get_current_context
from sqlalchemy import select, update, insert, true

from dags.model_lifecycle_orchestrator.on_promotion_decision.configs.airflow.data_keys import ArchiveKeys
from dags.model_lifecycle_orchestrator.on_promotion_decision.modules.schemas.airflow.configurations import PromotionDecisionCallbackConfigurations
from dags.shared.modules.schemas.airflow import AirflowTaskContext
from dags.shared.modules.schemas.postgres.model_deployment_workflows import ModelDeploymentWorkflows
from dags.shared.modules.schemas.postgres.model_deployments import ModelDeployments
from dags.shared.repositories.postgres.postgres import sql_session

@task.branch(task_id="promote_model_deployment")
def promote_model_deployment() -> None:
    context = get_current_context()

    promotion_decision_callback_configurations = PromotionDecisionCallbackConfigurations.from_context(context)

    with sql_session.begin() as session:
        project_id_subquery = (
            select(ModelDeploymentWorkflows.project_id)
            .where(ModelDeploymentWorkflows.id == promotion_decision_callback_configurations.workflow_id)
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
                    ModelDeploymentWorkflows.id == promotion_decision_callback_configurations.workflow_id
                )
            )
            .returning(
                ModelDeployments.dataset_max_timestamp
            )
        ).one().t

    ti = AirflowTaskContext.from_context(context).ti
    ti.xcom_push(
        key=ArchiveKeys.TRANSACTION_INFERENCES_ARCHIVE_CUTOFF_ISO_DATETIME,
        value=dataset_max_timestamp.isoformat()
    )