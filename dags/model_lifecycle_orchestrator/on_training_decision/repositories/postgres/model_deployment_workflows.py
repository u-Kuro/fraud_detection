from datetime import datetime

from airflow.sdk import task, get_current_context
from sqlalchemy import update, delete

from dags.model_lifecycle_orchestrator.on_training_decision.modules.schemas.airflow.configurations import TrainingDecisionCallbackConfigurations
from dags.model_lifecycle_orchestrator.on_training_decision.modules.schemas.airflow.xcom import UpdateTrainedModelInfoInWorkflowXCom, UpdatePromotionPendingWorkflow
from dags.shared.modules.configs.postgres import PostgresConfig
from dags.shared.modules.schemas.postgres.model_deployment_workflows import ModelDeploymentWorkflows
from dags.shared.repositories.postgres.postgres import sql_session

@task(task_id="update_approved_training_workflow")
def update_approved_training_workflow() -> None:
    context = get_current_context()

    training_decision_callback_configurations = TrainingDecisionCallbackConfigurations.from_context(context)

    with sql_session.begin() as session:
        session.execute(
            update(ModelDeploymentWorkflows.training_approved)
            .where(
                ModelDeploymentWorkflows.id == training_decision_callback_configurations.workflow_id,
                ModelDeploymentWorkflows.project_id == PostgresConfig.project_id()
            )
            .values({
                ModelDeploymentWorkflows.training_approved.key: True
            })
        )

@task(task_id="delete_rejected_training_workflow")
def delete_rejected_training_workflow() -> None:
    context = get_current_context()

    training_decision_callback_configurations = TrainingDecisionCallbackConfigurations.from_context(context)

    with sql_session.begin() as session:
        session.execute(
            delete(ModelDeploymentWorkflows)
            .where(
                ModelDeploymentWorkflows.id == training_decision_callback_configurations.workflow_id,
                ModelDeploymentWorkflows.project_id == PostgresConfig.project_id()
            )
        )

@task(task_id="update_trained_model_info_in_workflow")
def update_trained_model_info_in_workflow() -> None:
    context = get_current_context()

    training_decision_callback_configurations = TrainingDecisionCallbackConfigurations.from_context(context)
    update_trained_model_info_in_workflow_xcom = UpdateTrainedModelInfoInWorkflowXCom.from_context(context)

    with sql_session.begin() as session:
        session.execute(
            update(ModelDeploymentWorkflows)
            .where(
                ModelDeploymentWorkflows.id == training_decision_callback_configurations.workflow_id,
                ModelDeploymentWorkflows.project_id == PostgresConfig.project_id()
            )
            .values({
                ModelDeploymentWorkflows.model_trained_at.key: datetime.fromisoformat(update_trained_model_info_in_workflow_xcom.model_trained_at_iso_datetime),
                ModelDeploymentWorkflows.mlflow_run_id.key: update_trained_model_info_in_workflow_xcom.mlflow_run_id,
                ModelDeploymentWorkflows.registered_model_name.key: update_trained_model_info_in_workflow_xcom.model_name,
                ModelDeploymentWorkflows.registered_model_version.key: update_trained_model_info_in_workflow_xcom.model_version,
                ModelDeploymentWorkflows.model_dataset_min_timestamp.key: datetime.fromisoformat(update_trained_model_info_in_workflow_xcom.model_dataset_min_iso_datetime),
                ModelDeploymentWorkflows.model_dataset_max_timestamp.key: datetime.fromisoformat(update_trained_model_info_in_workflow_xcom.model_dataset_max_iso_datetime),
            })
        )

@task(task_id="update_promotion_pending_workflow")
def update_promotion_pending_workflow() -> None:
    context = get_current_context()

    training_decision_callback_configurations = TrainingDecisionCallbackConfigurations.from_context(context)
    update_promotion_pending_workflow_xcom = UpdatePromotionPendingWorkflow.from_context(context)

    with sql_session.begin() as session:
        session.execute(
            update(ModelDeploymentWorkflows)
            .where(
                ModelDeploymentWorkflows.id == training_decision_callback_configurations.workflow_id,
                ModelDeploymentWorkflows.project_id == PostgresConfig.project_id()
            )
            .values({
                ModelDeploymentWorkflows.promotion_approval_slack_ts.key: update_promotion_pending_workflow_xcom.promotion_approval_slack_ts
            })
        )