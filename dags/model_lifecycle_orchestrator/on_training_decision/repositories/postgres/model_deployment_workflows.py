from datetime import datetime

from airflow.sdk import task, get_current_context

from dags.model_lifecycle_orchestrator.on_training_decision.modules.schemas.airflow.configurations import TrainingDecisionCallbackConfigurations
from dags.model_lifecycle_orchestrator.on_training_decision.modules.schemas.airflow.xcom import UpdateTrainedModelInfoInWorkflowXCom, UpdatePromotionPendingWorkflow
from dags.shared.modules.configs.postgres import PostgresConfig
from dags.shared.modules.schemas.postgres.model_deployment_workflows import ModelDeploymentWorkflowsColumnKeys
from dags.shared.modules.schemas.postgres.postgres import PostgresTableKeys
from dags.shared.repositories.postgres.postgres import postgres_hook

@task.branch(task_id="update_approved_training_workflow")
def update_approved_training_workflow() -> None:
    context = get_current_context()

    training_decision_callback_configurations = TrainingDecisionCallbackConfigurations.from_context(context)

    postgres_hook.run(f"""
        UPDATE {PostgresTableKeys.model_deployment_workflows}
        SET {ModelDeploymentWorkflowsColumnKeys.training_approved} = %({ModelDeploymentWorkflowsColumnKeys.training_approved})s
        WHERE 
            {ModelDeploymentWorkflowsColumnKeys.id} = %({ModelDeploymentWorkflowsColumnKeys.id})s
        AND {ModelDeploymentWorkflowsColumnKeys.project_id} = %({ModelDeploymentWorkflowsColumnKeys.project_id})s
        """, parameters={
            ModelDeploymentWorkflowsColumnKeys.id: training_decision_callback_configurations.workflow_id,
            ModelDeploymentWorkflowsColumnKeys.project_id: PostgresConfig.PROJECT_ID(),
            ModelDeploymentWorkflowsColumnKeys.training_approved: True
        }
    )

@task.branch(task_id="delete_rejected_training_workflow")
def delete_rejected_training_workflow() -> None:
    context = get_current_context()

    training_decision_callback_configurations = TrainingDecisionCallbackConfigurations.from_context(context)

    postgres_hook.run(f"""
        DELETE FROM {PostgresTableKeys.model_deployment_workflows}
        WHERE 
            {ModelDeploymentWorkflowsColumnKeys.id} = %({ModelDeploymentWorkflowsColumnKeys.id})s
        AND {ModelDeploymentWorkflowsColumnKeys.project_id} = %({ModelDeploymentWorkflowsColumnKeys.project_id})s
        """, parameters={
            ModelDeploymentWorkflowsColumnKeys.id: training_decision_callback_configurations.workflow_id,
            ModelDeploymentWorkflowsColumnKeys.project_id: PostgresConfig.PROJECT_ID()
        }
    )

@task(task_id="update_trained_model_info_in_workflow")
def update_trained_model_info_in_workflow() -> None:
    context = get_current_context()

    training_decision_callback_configurations = TrainingDecisionCallbackConfigurations.from_context(context)
    update_trained_model_info_in_workflow_xcom = UpdateTrainedModelInfoInWorkflowXCom.from_context(context)

    postgres_hook.run(f"""
        UPDATE {PostgresTableKeys.model_deployment_workflows}
        SET {ModelDeploymentWorkflowsColumnKeys.model_trained_at} = %({ModelDeploymentWorkflowsColumnKeys.model_trained_at})s,
            {ModelDeploymentWorkflowsColumnKeys.mlflow_run_id} = %({ModelDeploymentWorkflowsColumnKeys.mlflow_run_id})s,
            {ModelDeploymentWorkflowsColumnKeys.registered_model_name} = %({ModelDeploymentWorkflowsColumnKeys.registered_model_name})s,
            {ModelDeploymentWorkflowsColumnKeys.registered_model_version} = %({ModelDeploymentWorkflowsColumnKeys.registered_model_version})s,
            {ModelDeploymentWorkflowsColumnKeys.model_dataset_min_timestamp} = %({ModelDeploymentWorkflowsColumnKeys.model_dataset_min_timestamp})s,
            {ModelDeploymentWorkflowsColumnKeys.model_dataset_max_timestamp} = %({ModelDeploymentWorkflowsColumnKeys.model_dataset_max_timestamp})s
        WHERE 
            {ModelDeploymentWorkflowsColumnKeys.id} = %({ModelDeploymentWorkflowsColumnKeys.id})s
        AND {ModelDeploymentWorkflowsColumnKeys.project_id} = %({ModelDeploymentWorkflowsColumnKeys.project_id})s
        """, parameters={
            ModelDeploymentWorkflowsColumnKeys.id: training_decision_callback_configurations.workflow_id,
            ModelDeploymentWorkflowsColumnKeys.project_id: PostgresConfig.PROJECT_ID(),
            ModelDeploymentWorkflowsColumnKeys.model_trained_at: datetime.fromisoformat(update_trained_model_info_in_workflow_xcom.model_trained_at_iso_datetime),
            ModelDeploymentWorkflowsColumnKeys.mlflow_run_id: update_trained_model_info_in_workflow_xcom.mlflow_run_id,
            ModelDeploymentWorkflowsColumnKeys.registered_model_name: update_trained_model_info_in_workflow_xcom.model_name,
            ModelDeploymentWorkflowsColumnKeys.registered_model_version: update_trained_model_info_in_workflow_xcom.model_version,
            ModelDeploymentWorkflowsColumnKeys.model_dataset_min_timestamp: datetime.fromisoformat(update_trained_model_info_in_workflow_xcom.model_dataset_min_iso_datetime),
            ModelDeploymentWorkflowsColumnKeys.model_dataset_max_timestamp: datetime.fromisoformat(update_trained_model_info_in_workflow_xcom.model_dataset_max_iso_datetime),
        }
    )

@task(task_id="update_promotion_pending_workflow")
def update_promotion_pending_workflow() -> None:
    context = get_current_context()

    training_decision_callback_configurations = TrainingDecisionCallbackConfigurations.from_context(context)
    update_promotion_pending_workflow_xcom = UpdatePromotionPendingWorkflow.from_context(context)

    postgres_hook.run(f"""
        UPDATE {PostgresTableKeys.model_deployment_workflows}
        SET {ModelDeploymentWorkflowsColumnKeys.promotion_approval_slack_ts} = %({ModelDeploymentWorkflowsColumnKeys.promotion_approval_slack_ts})s
        WHERE
            {ModelDeploymentWorkflowsColumnKeys.id} = %({ModelDeploymentWorkflowsColumnKeys.id})s
        AND {ModelDeploymentWorkflowsColumnKeys.project_id} = %({ModelDeploymentWorkflowsColumnKeys.project_id})s
        """, parameters={
            ModelDeploymentWorkflowsColumnKeys.id: training_decision_callback_configurations.workflow_id,
            ModelDeploymentWorkflowsColumnKeys.project_id: PostgresConfig.PROJECT_ID(),
            ModelDeploymentWorkflowsColumnKeys.promotion_approval_slack_ts: update_promotion_pending_workflow_xcom.promotion_approval_slack_ts
        }
    )