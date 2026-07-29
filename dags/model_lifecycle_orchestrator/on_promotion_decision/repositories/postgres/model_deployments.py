from datetime import datetime

from airflow.sdk import task, get_current_context

from dags.model_lifecycle_orchestrator.on_promotion_decision.configs.airflow.data_keys import ArchiveKeys
from dags.model_lifecycle_orchestrator.on_promotion_decision.modules.schemas.airflow.configurations import PromotionDecisionCallbackConfigurations
from dags.shared.modules.schemas.airflow import AirflowTaskContext
from dags.shared.modules.schemas.postgres.model_deployment_workflows import ModelDeploymentWorkflowsColumnKeys
from dags.shared.modules.schemas.postgres.model_deployments import ModelDeploymentsColumnKeys
from dags.shared.modules.schemas.postgres.postgres import PostgresTableKeys
from dags.shared.repositories.postgres import postgres_hook

@task.branch(task_id="promote_model_deployment")
def promote_model_deployment() -> None:
    context = get_current_context()

    promotion_decision_callback_configurations = PromotionDecisionCallbackConfigurations.from_context(context)

    with postgres_hook.get_conn() as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"""
                UPDATE {PostgresTableKeys.model_deployments}
                SET {ModelDeploymentsColumnKeys.active} = %({ModelDeploymentsColumnKeys.active})s
                WHERE
                    {ModelDeploymentsColumnKeys.project_id} = (
                        SELECT {ModelDeploymentWorkflowsColumnKeys.project_id}
                        FROM {PostgresTableKeys.model_deployment_workflows}
                        WHERE {ModelDeploymentWorkflowsColumnKeys.id} = %({ModelDeploymentWorkflowsColumnKeys.id})s
                    )
                AND {ModelDeploymentsColumnKeys.active}
                """, {
                    ModelDeploymentWorkflowsColumnKeys.id: promotion_decision_callback_configurations.workflow_id,
                    ModelDeploymentsColumnKeys.active: False
                }
            )

            cursor.execute(f"""
                INSERT INTO {PostgresTableKeys.model_deployments} (
                    {ModelDeploymentsColumnKeys.project_id},
                    {ModelDeploymentsColumnKeys.name},
                    {ModelDeploymentsColumnKeys.version},
                    {ModelDeploymentsColumnKeys.mlflow_run_id},
                    {ModelDeploymentsColumnKeys.dataset_min_timestamp},
                    {ModelDeploymentsColumnKeys.dataset_max_timestamp},
                    {ModelDeploymentsColumnKeys.active}
                )
                SELECT
                    {ModelDeploymentWorkflowsColumnKeys.project_id},
                    {ModelDeploymentWorkflowsColumnKeys.registered_model_name},
                    {ModelDeploymentWorkflowsColumnKeys.registered_model_version},
                    {ModelDeploymentWorkflowsColumnKeys.mlflow_run_id},
                    {ModelDeploymentWorkflowsColumnKeys.model_dataset_min_timestamp},
                    {ModelDeploymentWorkflowsColumnKeys.model_dataset_max_timestamp},
                    %({ModelDeploymentsColumnKeys.active})s
                FROM {PostgresTableKeys.model_deployment_workflows}
                WHERE {ModelDeploymentWorkflowsColumnKeys.id} = %({ModelDeploymentWorkflowsColumnKeys.id})s
                RETURNING {ModelDeploymentsColumnKeys.dataset_max_timestamp}
            """, {
                ModelDeploymentWorkflowsColumnKeys.id: promotion_decision_callback_configurations.workflow_id,
                ModelDeploymentsColumnKeys.active: True
            })

            dataset_max_timestamp: datetime = cursor.fetchone()[0]

            assert isinstance(dataset_max_timestamp, datetime)

    ti = AirflowTaskContext.from_context(context).ti
    ti.xcom_push(
        key=ArchiveKeys.TRANSACTION_INFERENCES_ARCHIVE_CUTOFF_ISO_DATETIME,
        value=dataset_max_timestamp.isoformat()
    )