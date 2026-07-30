from airflow.sdk import task, get_current_context
from sqlalchemy import update, select, insert, literal

from dags.model_lifecycle_orchestrator.on_promotion_decision.configs.airflow.data_keys import ArchiveKeys
from dags.model_lifecycle_orchestrator.on_promotion_decision.modules.schemas.airflow.configurations import PromotionDecisionCallbackConfigurations
from dags.shared.modules.schemas.airflow import AirflowTaskContext
from dags.shared.modules.schemas.postgres.model_deployment_workflows import ModelDeploymentWorkflow
from dags.shared.modules.schemas.postgres.model_deployments import ModelDeployment
from dags.shared.repositories.postgres.postgres import sql_session

@task.branch(task_id="promote_model_deployment")
def promote_model_deployment() -> None:
    context = get_current_context()

    promotion_decision_callback_configurations = PromotionDecisionCallbackConfigurations.from_context(context)

    with sql_session.begin() as session:
        project_id_subquery = (
            select(ModelDeploymentWorkflow.project_id)
            .where(ModelDeploymentWorkflow.id == promotion_decision_callback_configurations.workflow_id)
            .limit(1)
            .scalar_subquery()
        )
        session.execute(
            update(ModelDeployment)
            .where(
                ModelDeployment.project_id == project_id_subquery,
                ModelDeployment.active.is_(True)
            )
            .values({
                ModelDeployment.active.key: False
            })
        )

        (dataset_max_timestamp,) = session.execute(
            insert(ModelDeployment)
            .from_select(
                (
                    ModelDeployment.project_id,
                    ModelDeployment.name,
                    ModelDeployment.version,
                    ModelDeployment.mlflow_run_id,
                    ModelDeployment.dataset_min_timestamp,
                    ModelDeployment.dataset_max_timestamp,
                    ModelDeployment.active
                ),
                select(
                    ModelDeploymentWorkflow.project_id,
                    ModelDeploymentWorkflow.registered_model_name,
                    ModelDeploymentWorkflow.registered_model_version,
                    ModelDeploymentWorkflow.mlflow_run_id,
                    ModelDeploymentWorkflow.model_dataset_min_timestamp,
                    ModelDeploymentWorkflow.model_dataset_max_timestamp,
                    literal(True)
                )
                .where(
                    ModelDeploymentWorkflow.id == promotion_decision_callback_configurations.workflow_id
                )
            )
            .returning(
                ModelDeployment.dataset_max_timestamp
            )
        ).one().t

    ti = AirflowTaskContext.from_context(context).ti
    ti.xcom_push(
        key=ArchiveKeys.TRANSACTION_INFERENCES_ARCHIVE_CUTOFF_ISO_DATETIME,
        value=dataset_max_timestamp.isoformat()
    )