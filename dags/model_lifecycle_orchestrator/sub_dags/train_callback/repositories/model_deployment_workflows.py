from airflow.sdk import task

from dags.model_lifecycle_orchestrator.sub_dags.train_callback.modules.schemas.airflow.configurations import TrainingCallbackConfigurations
from dags.model_lifecycle_orchestrator.sub_dags.train_callback.services.training_callback import start_training_pipeline
from dags.shared.modules.configs.postgres import PostgresConfig
from dags.shared.modules.schemas.postgres.model_deployment_workflows import ModelDeploymentWorkflowsColumnKeys
from dags.shared.modules.schemas.postgres.postgres import PostgresTableKeys
from dags.shared.repositories.postgres import postgres_hook


@task.branch(task_id="update_approved_training_workflow")
def update_approved_training_workflow(**context) -> str:
    training_callback_configurations = TrainingCallbackConfigurations.from_context(context)

    postgres_hook.run(f"""
        UPDATE {PostgresTableKeys.model_deployment_workflows}
        SET {ModelDeploymentWorkflowsColumnKeys.training_approved} = %(training_approved)s
        WHERE 
            {ModelDeploymentWorkflowsColumnKeys.id} = %(id)s
        AND {ModelDeploymentWorkflowsColumnKeys.project_id} = %(project_id)s
        """, parameters={
            "id": training_callback_configurations.workflow_id,
            "project_id": PostgresConfig.PROJECT_ID,
            "training_approved": True
        }
    )

    return start_training_pipeline.__name__

@task.branch(task_id="delete_rejected_training_workflow")
def delete_rejected_training_workflow(**context):
    training_callback_configurations = TrainingCallbackConfigurations.from_context(context)

    postgres_hook.run(f"""
        DELETE FROM {PostgresTableKeys.model_deployment_workflows} 
        WHERE 
            {ModelDeploymentWorkflowsColumnKeys.id} = %(id)s
        AND {ModelDeploymentWorkflowsColumnKeys.project_id} = %(project_id)s
        """, parameters={
            "id": training_callback_configurations.workflow_id,
            "project_id": PostgresConfig.PROJECT_ID
        }
    )