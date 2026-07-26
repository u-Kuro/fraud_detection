from airflow.sdk import task

from dags.model_lifecycle_orchestrator.on_promotion_decision.modules.schemas.airflow.configurations import PromotionDecisionCallbackConfigurations
from dags.shared.modules.schemas.postgres.model_deployment_workflows import ModelDeploymentWorkflowsColumnKeys
from dags.shared.modules.schemas.postgres.model_deployments import ModelDeploymentsColumnKeys
from dags.shared.modules.schemas.postgres.postgres import PostgresTableKeys
from dags.shared.repositories.postgres import postgres_hook

@task.branch(task_id="promote_model_deployment")
def promote_model_deployment(**context) -> None:
    promotion_decision_callback_configurations = PromotionDecisionCallbackConfigurations.from_context(context)

    with postgres_hook.get_conn() as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"""
                UPDATE {PostgresTableKeys.model_deployments}
                SET {ModelDeploymentsColumnKeys.active} = %(active)s
                WHERE
                    {ModelDeploymentsColumnKeys.project_id} = (
                        SELECT {ModelDeploymentWorkflowsColumnKeys.project_id}
                        FROM {PostgresTableKeys.model_deployment_workflows}
                        WHERE id = %(workflow_id)s
                    )
                AND {ModelDeploymentsColumnKeys.active}
                """, {
                    "workflow_id": promotion_decision_callback_configurations.workflow_id,
                    "active": False
                }
            )

            cursor.execute(f"""
                INSERT INTO {PostgresTableKeys.model_deployments} (
                    project_id,
                    name,
                    version,
                    mlflow_run_id,
                    dataset_min_timestamp,
                    dataset_max_timestamp,
                    active
                )
                SELECT
                    project_id,
                    registered_model_name,
                    registered_model_version,
                    mlflow_run_id,
                    model_dataset_min_timestamp,
                    model_dataset_max_timestamp,
                    %(active)s
                FROM {PostgresTableKeys.model_deployment_workflows}
                WHERE id = %(workflow_id)s
            """, {
                "workflow_id": promotion_decision_callback_configurations.workflow_id,
                "active": True
            })