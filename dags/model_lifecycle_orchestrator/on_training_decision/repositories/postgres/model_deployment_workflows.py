from airflow.sdk import task
from sqlalchemy import update, delete

from dags.model_lifecycle_orchestrator.on_training_decision.modules.schemas.airflow.tasks import TrainingDecision, ModelDeploymentWorkflowForPromotion
from dags.model_lifecycle_orchestrator.on_training_decision.modules.schemas.airflow.xcom import TrainModelResult
from dags.shared.modules.configs.postgres import PostgresConfig
from dags.shared.modules.schemas.postgres.model_deployment_workflows import ModelDeploymentWorkflows
from dags.shared.repositories.postgres.postgres import sql_session

@task
def update_approved_training_workflow(training_decision: TrainingDecision):
    with sql_session.begin() as session:
        session.execute(
            update(ModelDeploymentWorkflows.training_approved)
            .where(
                ModelDeploymentWorkflows.id == training_decision.model_deployment_workflow.id,
                ModelDeploymentWorkflows.project_id == PostgresConfig.project_id()
            )
            .values({
                ModelDeploymentWorkflows.training_approved.key: True
            })
        )

@task
def update_trained_model_info_in_workflow(
    training_decision: TrainingDecision,
    train_model_result: TrainModelResult,
):
    with sql_session.begin() as session:
        session.execute(
            update(ModelDeploymentWorkflows)
            .where(
                ModelDeploymentWorkflows.id == training_decision.model_deployment_workflow.id,
                ModelDeploymentWorkflows.project_id == PostgresConfig.project_id()
            )
            .values({
                ModelDeploymentWorkflows.model_trained_at.key: train_model_result.model_trained_at_datetime,
                ModelDeploymentWorkflows.mlflow_run_id.key: train_model_result.model_mlflow_run_id,
                ModelDeploymentWorkflows.registered_model_name.key: train_model_result.model_name,
                ModelDeploymentWorkflows.registered_model_version.key: train_model_result.model_version,
                ModelDeploymentWorkflows.model_dataset_min_timestamp.key: train_model_result.model_dataset_min_datetime,
                ModelDeploymentWorkflows.model_dataset_max_timestamp.key: train_model_result.model_dataset_max_datetime,
            })
        )

@task
def update_promotion_pending_workflow(
    training_decision: TrainingDecision,
    model_deployment_workflow_for_promotion: ModelDeploymentWorkflowForPromotion,
):
    with sql_session.begin() as session:
        session.execute(
            update(ModelDeploymentWorkflows)
            .where(
                ModelDeploymentWorkflows.id == training_decision.model_deployment_workflow.id,
                ModelDeploymentWorkflows.project_id == PostgresConfig.project_id()
            )
            .values({
                ModelDeploymentWorkflows.slack_promotion_approval_message_ts.key: model_deployment_workflow_for_promotion.slack_promotion_approval_message_ts
            })
        )

@task
def delete_rejected_training_workflow(training_decision: TrainingDecision):
    with sql_session.begin() as session:
        session.execute(
            delete(ModelDeploymentWorkflows)
            .where(
                ModelDeploymentWorkflows.id == training_decision.model_deployment_workflow.id,
                ModelDeploymentWorkflows.project_id == PostgresConfig.project_id()
            )
        )
