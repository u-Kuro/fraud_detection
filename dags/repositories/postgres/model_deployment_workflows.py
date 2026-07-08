from uuid import UUID

from airflow.sdk import task

from dags.controllers.slack import post_cold_start_training_approval
from dags.modules.configs import postgres_config
from dags.modules.configs.postgres import model_deployment_workflows_config
from dags.modules.schemas.airflow import CreateTrainPendingWorkflowConfigurations
from dags.modules.schemas.model_deployment_workflow import ModelDeploymentWorkflow, ModelDeploymentWorkflowState
from dags.repositories.postgres import postgres_hook
from dags.services.airflow_operators import no_action

@task.branch(task_id="has_expired_promote_pending_workflow_with_replacement")
def has_expired_promote_pending_workflow_with_replacement() -> str:
    result = postgres_hook.get_first("""
        SELECT EXISTS (
            SELECT 1
            FROM model_deployment_workflows
            WHERE
                project_id = %(project_id)s
            AND state = %(promote_pending_state)s
            AND trained_at < NOW() - %(TRAINED_MODEL_EXPIRATION_DAYS)s * INTERVAL '1 day'
        )
        AND EXISTS (
            SELECT 1
            FROM model_deployment_workflows
            WHERE
                project_id = %(project_id)s
            AND state = %(promote_pending_replacement_state)s
        )
        """, {
            "project_id": postgres_config.PROJECT_ID,
            "promote_pending_state": ModelDeploymentWorkflowState.promote_pending,
            "promote_pending_replacement_state": ModelDeploymentWorkflowState.promote_pending_replacement,
            "TRAINED_MODEL_EXPIRATION_DAYS": model_deployment_workflows_config.TRAINED_MODEL_EXPIRATION_DAYS,
        }
    )
    workflows_exists = bool(result[0])

    if workflows_exists:
        return replace_challenger_model.__name__
    else:
        return no_action.__name__

def get_current_model_deployment_workflow() -> ModelDeploymentWorkflow | None:
    model_deployment_workflow_keys = ModelDeploymentWorkflow.model_field_keys()
    model_deployment_workflow_row = postgres_hook.get_first(f"""
        SELECT {",".join(model_deployment_workflow_keys)}
        FROM model_deployment_workflows
        WHERE project_id = %(project_id)s
        ORDER BY created_at DESC
        LIMIT 1
        """, {
            "project_id": postgres_config.PROJECT_ID
        }
    )

    if model_deployment_workflow_row is None:
        return None
    else:
        model_deployment_workflow = dict(zip(model_deployment_workflow_keys, model_deployment_workflow_row))
        return ModelDeploymentWorkflow.model_validate(
            model_deployment_workflow,
            from_attributes=True
        )

@task.branch(task_id="has_no_ongoing_model_deployment_workflow")
def has_no_ongoing_model_deployment_workflow() -> str:
    if get_current_model_deployment_workflow() is None:
        return post_cold_start_training_approval.__name__
    else:
        return no_action.__name__

@task(task_id="create_train_pending_workflow")
def create_train_pending_workflow(**context) -> None:
    configurations = CreateTrainPendingWorkflowConfigurations.from_context(context)

    postgres_hook.run("""
        INSERT INTO model_deployment_workflows (
            id,
            project_id,
            state,
            training_approved,
            training_approval_slack_ts
        )
        VALUES (
            %(id)s,
            %(project_id)s,
            %(state)s,
            %(training_approved)s,
            %(training_approval_slack_ts)s
        )
        """, parameters={
            "id": configurations.workflow_id,
            "project_id": postgres_config.PROJECT_ID,
            "state": ModelDeploymentWorkflowState.train_pending,
            "training_approved": False,
            "training_approval_slack_ts": configurations.training_approval_slack_ts,
        }
    )

def update_training_approval_slack_ts(training_approval_slack_ts: str | None, current_model_deployment_workflow: ModelDeploymentWorkflow) -> None:
    with engine.connect() as connection:
        connection.execute(text("""
            UPDATE model_deployment_workflows
            SET training_approval_slack_ts = :training_approval_slack_ts
            WHERE id = :id
        """),{
            "id": current_model_deployment_workflow.id,
            "training_approval_slack_ts": training_approval_slack_ts
        })
        connection.commit()

def training_approved(workflow_id: UUID):
    with engine.begin() as connection:
        connection.execute(text("""
            UPDATE model_deployment_workflows
            SET training_approved = :training_approved
            WHERE id = :id
        """), {
            "id": workflow_id,
            "training_approved": True
        })

def promotion_approved(workflow_id: UUID):
    with engine.begin() as connection:
        connection.execute(text("""
            UPDATE model_deployment_workflows
            SET promotion_approved = :promotion_approved
            WHERE id = :id
        """), {
            "id": workflow_id,
            "promotion_approved": True
        })

def workflow_rejected(workflow_id: UUID):
    with engine.begin() as connection:
        connection.execute(text("""
            DELETE FROM model_deployment_workflows
            WHERE id = :id
        """), {
            "id": workflow_id
        })