from uuid import UUID

from airflow.sdk import task, get_current_context
from sqlalchemy import select, func, literal, cast, true, delete, insert, update
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.orm import aliased

from dags.model_lifecycle_orchestrator.check_training_need.controllers.slack import invalidate_old_training_approval, invalidate_expired_promotion_approval
from dags.model_lifecycle_orchestrator.check_training_need.modules.configs.airflow.data_keys import ExpiredModelDeploymentWorkflowsKeys, ReservedModelDeploymentWorkflowsKeys
from dags.model_lifecycle_orchestrator.check_training_need.modules.configs.airflow.task_states import CurrentModelDeploymentWorkflowForTrainingStates
from dags.model_lifecycle_orchestrator.check_training_need.modules.configs.postgres.model_deployment_workflows import ModelDeploymentWorkflowsConfig
from dags.model_lifecycle_orchestrator.check_training_need.modules.configs.airflow.task_ids import NoActionTaskIDs
from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.airflow.tasks import ExpiredModelDeploymentWorkflowWithItsReplacement, ModelDeploymentWorkflowForTraining, ExpiredModelDeploymentWorkflow, ReservedModelDeploymentWorkflow
from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.model_deployment_workflows import ModelDeploymentWorkflow
from dags.shared.modules.configs.postgres import PostgresConfig
from dags.shared.modules.schemas.airflow import TaskContext
from dags.shared.modules.schemas.postgres.model_deployment_workflows import ModelDeploymentWorkflows, ModelDeploymentWorkflowState
from dags.shared.repositories.postgres.postgres import sql_session

@task
def get_expired_model_deployment_workflow_with_its_replacement() -> ExpiredModelDeploymentWorkflowWithItsReplacement | None:
    with sql_session.begin() as session:
        expired_model_deployment_workflow = aliased(
            ModelDeploymentWorkflows,
            select(ModelDeploymentWorkflows)
            .where(
                ModelDeploymentWorkflows.project_id == PostgresConfig.project_id(),
                ModelDeploymentWorkflows.state == ModelDeploymentWorkflowState.promote_pending,
                ModelDeploymentWorkflows.model_trained_at <= func.now() - (
                    literal(ModelDeploymentWorkflowsConfig.challenger_model_expiration_days)
                    * cast(literal("1 day"), INTERVAL)
                )
            )
            .subquery(name="expired_model_deployment_workflow")
        )
        reserved_model_deployment_workflow = aliased(
            ModelDeploymentWorkflows,
            select(ModelDeploymentWorkflows)
            .where(
                ModelDeploymentWorkflows.project_id == PostgresConfig.project_id(),
                ModelDeploymentWorkflows.state == ModelDeploymentWorkflowState.reserved
            )
            .subquery(name="reserved_model_deployment_workflow")
        )

        result = session.execute(
            select(
                expired_model_deployment_workflow.id.label(ExpiredModelDeploymentWorkflowsKeys.WORKFLOW_ID),
                expired_model_deployment_workflow.registered_model_name.label(ExpiredModelDeploymentWorkflowsKeys.MODEL_NAME),
                expired_model_deployment_workflow.registered_model_version.label(ExpiredModelDeploymentWorkflowsKeys.MODEL_VERSION),
                expired_model_deployment_workflow.mlflow_run_id.label(ExpiredModelDeploymentWorkflowsKeys.MLFLOW_RUN_ID),
                expired_model_deployment_workflow.promotion_approval_slack_ts.label(ExpiredModelDeploymentWorkflowsKeys.PROMOTION_APPROVAL_SLACK_TS),

                reserved_model_deployment_workflow.registered_model_name.label(ReservedModelDeploymentWorkflowsKeys.MODEL_NAME),
                reserved_model_deployment_workflow.registered_model_version.label(ReservedModelDeploymentWorkflowsKeys.MODEL_VERSION),
            ).join_from(
                expired_model_deployment_workflow,
                reserved_model_deployment_workflow,
                onclause=true()
            )
            .limit(1)
        ).mappings().first()

    if result is None:
        return None
    else:
        return ExpiredModelDeploymentWorkflowWithItsReplacement(
            expired=ExpiredModelDeploymentWorkflow(
                workflow_id=result[ExpiredModelDeploymentWorkflowsKeys.WORKFLOW_ID],
                model_name=result[ExpiredModelDeploymentWorkflowsKeys.MODEL_NAME],
                model_version=result[ExpiredModelDeploymentWorkflowsKeys.MODEL_VERSION],
                mlflow_run_id=result[ExpiredModelDeploymentWorkflowsKeys.MLFLOW_RUN_ID],
                promotion_approval_slack_ts=result[ExpiredModelDeploymentWorkflowsKeys.PROMOTION_APPROVAL_SLACK_TS],
            ),
            reserved=ReservedModelDeploymentWorkflow(
                model_name=result[ReservedModelDeploymentWorkflowsKeys.MODEL_NAME],
                model_version=result[ReservedModelDeploymentWorkflowsKeys.MODEL_VERSION],
            )
        )

@task.branch
def has_expired_promote_pending_workflow_with_replacement(data: ExpiredModelDeploymentWorkflowWithItsReplacement | None) -> str:
    context = TaskContext(get_current_context())

    if data is None:
        return context.resolve_task_id(
            task_id=NoActionTaskIDs.no_expired_promote_pending_workflow_with_replacement
        )
    else:
        return context.resolve_task_id(
            task_id=invalidate_expired_promotion_approval.__name__
        )

@task
def get_current_model_deployment_workflow_for_training() -> ModelDeploymentWorkflowForTraining | None:
    with sql_session.begin() as session:
        model_deployment_workflow_rows = session.execute(
            select(ModelDeploymentWorkflows)
            .where(
                ModelDeploymentWorkflows.project_id == PostgresConfig.project_id()
            )
            .order_by(
                ModelDeploymentWorkflows.created_at.desc()
            )
            .limit(2)
        ).mappings().all()

    current_model_deployment_workflows = [
        ModelDeploymentWorkflow.model_validate(row)
        for row in model_deployment_workflow_rows
    ]

    current_model_deployment_workflows_length = len(current_model_deployment_workflows)
    if current_model_deployment_workflows_length == 0:
        return ModelDeploymentWorkflowForTraining(
            state=CurrentModelDeploymentWorkflowForTrainingStates.train_the_challenger,
            should_train_for_promotion=True,
        )
    elif current_model_deployment_workflows_length == 1:
        latest_workflow = current_model_deployment_workflows.pop()
        if latest_workflow.state == ModelDeploymentWorkflowState.train_pending:
            return ModelDeploymentWorkflowForTraining(
                state=CurrentModelDeploymentWorkflowForTrainingStates.train_and_replace_the_challenger,
                workflow_id=latest_workflow.id,
                training_approval_slack_ts=latest_workflow.training_approval_slack_ts,
                should_train_for_promotion=True,
            )
        elif latest_workflow.state == ModelDeploymentWorkflowState.promote_pending:
            return ModelDeploymentWorkflowForTraining(
                state=CurrentModelDeploymentWorkflowForTrainingStates.train_the_challenger_substitute,
                should_train_for_promotion=False,
            )
        else:
            raise ValueError(f"Unexpected workflow state with 1 active workflow: {latest_workflow.state!r}")
    elif current_model_deployment_workflows_length == 2:
        oldest_workflow = current_model_deployment_workflows.pop()
        if oldest_workflow.state != ModelDeploymentWorkflowState.promote_pending:
            raise ValueError(f"Expected oldest workflow state to be promote_pending, got: {oldest_workflow.state!r}")

        latest_workflow = current_model_deployment_workflows.pop()
        if latest_workflow.state == ModelDeploymentWorkflowState.train_pending:
            return ModelDeploymentWorkflowForTraining(
                state=CurrentModelDeploymentWorkflowForTrainingStates.train_and_replace_the_challenger_substitute,
                workflow_id=latest_workflow.id,
                training_approval_slack_ts=latest_workflow.training_approval_slack_ts,
                should_train_for_promotion=True,
            )
        elif latest_workflow.state == ModelDeploymentWorkflowState.reserved:
            return None
        else:
            raise ValueError(f"Unexpected workflow state with 2 active workflows: {latest_workflow.state!r}")
    else:
        raise ValueError(f"Unexpected number of active workflows: {current_model_deployment_workflows_length}")

@task.branch
def check_current_model_deployment_workflows(model_deployment_workflow_for_training: ModelDeploymentWorkflowForTraining | None) -> str:
    context = TaskContext(get_current_context())
    if model_deployment_workflow_for_training is None:
        return context.resolve_task_id(
            task_id=NoActionTaskIDs.no_expired_workflows
        )
    else:
        match model_deployment_workflow_for_training.state:
            case CurrentModelDeploymentWorkflowForTrainingStates.train_the_challenger:
                return context.resolve_task_id(
                    task_id=initialize_train_pending_workflow.__name__
                )
            case CurrentModelDeploymentWorkflowForTrainingStates.train_and_replace_the_challenger:
                return context.resolve_task_id(
                    task_id=invalidate_old_training_approval.__name__
                )
            case CurrentModelDeploymentWorkflowForTrainingStates.train_the_challenger_substitute:
                return context.resolve_task_id(
                    task_id=initialize_train_pending_workflow.__name__
                )
            case CurrentModelDeploymentWorkflowForTrainingStates.train_and_replace_the_challenger_substitute:
                return context.resolve_task_id(
                    task_id=invalidate_old_training_approval.__name__
                )
        raise ValueError(f"Unexpected state: {model_deployment_workflow_for_training.state}")

@task
def delete_expired_promote_pending_workflow(data: ExpiredModelDeploymentWorkflowWithItsReplacement | None) -> None:
    assert isinstance(data, ExpiredModelDeploymentWorkflowWithItsReplacement)

    with sql_session.begin() as session:
        session.execute(
            delete(ModelDeploymentWorkflows)
            .where(
                ModelDeploymentWorkflows.id == data.expired.workflow_id,
                ModelDeploymentWorkflows.project_id == PostgresConfig.project_id(),
                ModelDeploymentWorkflows.state == ModelDeploymentWorkflowState.promote_pending
            )
        )

@task
def initialize_train_pending_workflow(model_deployment_workflow_for_training: ModelDeploymentWorkflowForTraining | None) -> ModelDeploymentWorkflowForTraining:
    assert isinstance(model_deployment_workflow_for_training, ModelDeploymentWorkflowForTraining)

    with sql_session.begin() as session:
        (workflow_id,) = session.execute(
            insert(ModelDeploymentWorkflows)
            .values({
                ModelDeploymentWorkflows.project_id.key: PostgresConfig.project_id(),
                ModelDeploymentWorkflows.state.key: ModelDeploymentWorkflowState.train_pending
            })
            .returning(
                ModelDeploymentWorkflows.id
            )
        ).one().t

    assert isinstance(workflow_id, UUID)

    model_deployment_workflow_for_training.workflow_id = workflow_id

    return model_deployment_workflow_for_training

@task
def reinitialize_train_pending_workflow(model_deployment_workflow_for_training: ModelDeploymentWorkflowForTraining | None) -> None:
    assert model_deployment_workflow_for_training is not None
    assert model_deployment_workflow_for_training.workflow_id is not None

    with sql_session.begin() as session:
        session.execute(
            update(ModelDeploymentWorkflows)
            .where(
                ModelDeploymentWorkflows.id == model_deployment_workflow_for_training.workflow_id,
                ModelDeploymentWorkflows.project_id == PostgresConfig.project_id(),
                ModelDeploymentWorkflows.state == ModelDeploymentWorkflowState.train_pending
            )
            .values({
                ModelDeploymentWorkflows.created_at.key: func.now(),
                ModelDeploymentWorkflows.state.key: ModelDeploymentWorkflowState.train_pending
            })
        )

@task
def update_train_pending_workflow(model_deployment_workflow_for_training: ModelDeploymentWorkflowForTraining) -> None:
    assert model_deployment_workflow_for_training.training_approval_slack_ts is not None

    with sql_session.begin() as session:
        session.execute(
            update(ModelDeploymentWorkflows)
            .where(
                ModelDeploymentWorkflows.id == model_deployment_workflow_for_training.workflow_id,
                ModelDeploymentWorkflows.project_id == PostgresConfig.project_id()
            )
            .values({
                ModelDeploymentWorkflows.training_approval_slack_ts.key: model_deployment_workflow_for_training.training_approval_slack_ts
            })
        )