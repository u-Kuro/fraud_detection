from airflow.sdk import task

from dags.drift_monitor.controllers.slack import post_retraining_approval, update_retraining_approval, post_cold_start_training_approval
from dags.drift_monitor.modules.configs.airflow import DriftMonitorKeys
from dags.drift_monitor.modules.configs.postgres import model_deployment_workflows_config

from dags.drift_monitor.modules.schemas.airflow.xcom import CreateTrainPendingWorkflowXCom, CheckCurrentModelDeploymentWorkflowXCom, UpdateRetrainingPendingWorkflowXCom
from dags.drift_monitor.modules.schemas.model_deployment_workflows import ModelDeploymentWorkflows, ModelDeploymentWorkflowState
from dags.drift_monitor.repositories.mlflow.registered_model import replace_challenger_model

from dags.shared.modules.configs import postgres_config
from dags.shared.modules.configs.airflow import ModelDeploymentWorkflowsKeys
from dags.shared.modules.schemas.airflow import AirflowTaskContext
from dags.shared.repositories.postgres import postgres_hook
from dags.shared.services.airflow_operators import no_action

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

def get_current_model_deployment_workflow() -> ModelDeploymentWorkflows | None:
    model_deployment_workflow_keys = ModelDeploymentWorkflows.model_field_keys()
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
        return ModelDeploymentWorkflows.model_validate(
            model_deployment_workflow,
            from_attributes=True
        )

@task.branch(task_id="check_current_model_deployment_workflow")
def check_current_model_deployment_workflow(**context) -> str:
    check_current_model_deployment_workflow_xcom = CheckCurrentModelDeploymentWorkflowXCom.from_context(context)

    current_model_deployment_workflow = get_current_model_deployment_workflow()

    if current_model_deployment_workflow is None:
        branch = post_retraining_approval.__name__
    elif current_model_deployment_workflow.state == ModelDeploymentWorkflowState.train_pending:
        branch = update_retraining_approval.__name__
    else:
        branch = no_action.__name__

    if branch != no_action.__name__:
        ti = AirflowTaskContext.from_context(context).ti
        ti.xcom_push(
            key=DriftMonitorKeys.DRIFT_SUMMARY_KEY,
            value=check_current_model_deployment_workflow_xcom.drift_summary,
        )
        if branch == update_retraining_approval.__name__:
            assert current_model_deployment_workflow is not None
            ti.xcom_push(
                key=ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID_KEY,
                value=str(current_model_deployment_workflow.id),
            )
            ti.xcom_push(
                key=ModelDeploymentWorkflowsKeys.TRAINING_APPROVAL_SLACK_TS_KEY,
                value=current_model_deployment_workflow.training_approval_slack_ts,
            )

    return branch

@task(task_id="create_train_pending_workflow")
def create_train_pending_workflow(**context) -> None:
    create_train_pending_workflow_xcom = CreateTrainPendingWorkflowXCom.from_context(context)

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
            "id": create_train_pending_workflow_xcom.workflow_id,
            "project_id": postgres_config.PROJECT_ID,
            "state": ModelDeploymentWorkflowState.train_pending,
            "training_approved": False,
            "training_approval_slack_ts": create_train_pending_workflow_xcom.training_approval_slack_ts,
        }
    )

@task(task_id="update_training_pending_workflow")
def update_training_pending_workflow(**context) -> None:
    update_training_pending_workflow_xcom = UpdateRetrainingPendingWorkflowXCom.from_context(context)

    postgres_hook.run("""
        UPDATE model_deployment_workflows
        SET training_approval_slack_ts = %(training_approval_slack_ts)s
        WHERE id = %(id)s
    """, parameters={
        "id": update_training_pending_workflow_xcom.workflow_id,
        "training_approval_slack_ts": update_training_pending_workflow_xcom.training_approval_slack_ts
    })

@task.branch(task_id="has_no_ongoing_model_deployment_workflow")
def has_no_ongoing_model_deployment_workflow() -> str:
    if get_current_model_deployment_workflow() is None:
        return post_cold_start_training_approval.__name__
    else:
        return no_action.__name__
#
# def training_approved(workflow_id: UUID):
#     with engine.begin() as connection:
#         connection.execute(text("""
#             UPDATE model_deployment_workflows
#             SET training_approved = :training_approved
#             WHERE id = :id
#         """), {
#             "id": workflow_id,
#             "training_approved": True
#         })
#
# def promotion_approved(workflow_id: UUID):
#     with engine.begin() as connection:
#         connection.execute(text("""
#             UPDATE model_deployment_workflows
#             SET promotion_approved = :promotion_approved
#             WHERE id = :id
#         """), {
#             "id": workflow_id,
#             "promotion_approved": True
#         })
#
# def workflow_rejected(workflow_id: UUID):
#     with engine.begin() as connection:
#         connection.execute(text("""
#             DELETE FROM model_deployment_workflows
#             WHERE id = :id
#         """), {
#             "id": workflow_id
#         })