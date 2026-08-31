from uuid import UUID

from airflow.sdk import task, get_current_context
from sqlalchemy import select, func, literal, cast, true, delete, insert, update
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.orm import aliased

from dags.model_lifecycle_orchestrator.check_training_need.controllers.slack import invalidate_old_training_approval, invalidate_expired_promotion_approval
from dags.model_lifecycle_orchestrator.check_training_need.modules.configs.airflow.task_states import CurrentModelDeploymentWorkflowForTrainingStates
from dags.model_lifecycle_orchestrator.check_training_need.modules.configs.postgres.model_deployment_workflows import ModelDeploymentWorkflowsConfig, ReservedModelDeploymentWorkflowLabels, ExpiredModelDeploymentWorkflowsLabels
from dags.model_lifecycle_orchestrator.check_training_need.modules.configs.airflow.task_ids import NoActionTaskIDs
from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.airflow.tasks import ExpiredAndReservedModelDeploymentWorkflows, ModelDeploymentWorkflowForTraining, ExpiredModelDeploymentWorkflow, ReservedModelDeploymentWorkflow
from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.model_deployment_workflows import ModelDeploymentWorkflow
from dags.shared.modules.configs.postgres import PostgresConfig
from dags.shared.modules.schemas.airflow import TaskContext
from dags.shared.modules.schemas.postgres.model_deployment_workflows import ModelDeploymentWorkflows, ModelDeploymentWorkflowState
from dags.shared.repositories.postgres.postgres import sql_session

@task
def get_expired_model_deployment_workflow_with_its_replacement() -> ExpiredAndReservedModelDeploymentWorkflows | None:
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
            .subquery()
        )
        reserved_model_deployment_workflow = aliased(
            ModelDeploymentWorkflows,
            select(ModelDeploymentWorkflows)
            .where(
                ModelDeploymentWorkflows.project_id == PostgresConfig.project_id(),
                ModelDeploymentWorkflows.state == ModelDeploymentWorkflowState.reserved
            )
            .subquery()
        )

        result = session.execute(
            select(
                expired_model_deployment_workflow.id.label(ExpiredModelDeploymentWorkflowsLabels.id),
                expired_model_deployment_workflow.registered_model_name.label(ExpiredModelDeploymentWorkflowsLabels.registered_model_name),
                expired_model_deployment_workflow.registered_model_version.label(ExpiredModelDeploymentWorkflowsLabels.registered_model_version),
                expired_model_deployment_workflow.mlflow_run_id.label(ExpiredModelDeploymentWorkflowsLabels.mlflow_run_id),
                expired_model_deployment_workflow.slack_promotion_approval_message_ts.label(ExpiredModelDeploymentWorkflowsLabels.slack_promotion_approval_message_ts),

                reserved_model_deployment_workflow.registered_model_name.label(ReservedModelDeploymentWorkflowLabels.registered_model_name),
                reserved_model_deployment_workflow.registered_model_version.label(ReservedModelDeploymentWorkflowLabels.registered_model_version),
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
        return ExpiredAndReservedModelDeploymentWorkflows(
            expired=ExpiredModelDeploymentWorkflow(
                id=result[ExpiredModelDeploymentWorkflowsLabels.id],
                model_name=result[ExpiredModelDeploymentWorkflowsLabels.registered_model_name],
                model_version=result[ExpiredModelDeploymentWorkflowsLabels.registered_model_version],
                mlflow_run_id=result[ExpiredModelDeploymentWorkflowsLabels.mlflow_run_id],
                slack_promotion_approval_message_ts=result[ExpiredModelDeploymentWorkflowsLabels.slack_promotion_approval_message_ts],
            ),
            reserved=ReservedModelDeploymentWorkflow(
                model_name=result[ReservedModelDeploymentWorkflowLabels.registered_model_name],
                model_version=result[ReservedModelDeploymentWorkflowLabels.registered_model_version],
            )
        )

@task.branch
def has_expired_promote_pending_workflow_with_replacement(expired_and_reserved_model_deployment_workflows: ExpiredAndReservedModelDeploymentWorkflows | None) -> str:
    context = TaskContext(get_current_context())

    if expired_and_reserved_model_deployment_workflows is None:
        return context.resolve_task_id(
            task_id=NoActionTaskIDs.no_expired_promote_pending_workflow_with_replacement
        )
    else:
        return context.resolve_task_id(
            task_id=invalidate_expired_promotion_approval.__name__
        )

@task
def delete_expired_promote_pending_workflow(model_deployment_workflows: ExpiredAndReservedModelDeploymentWorkflows | None):
    assert model_deployment_workflows is not None

    with sql_session.begin() as session:
        session.execute(
            delete(ModelDeploymentWorkflows)
            .where(
                ModelDeploymentWorkflows.id == model_deployment_workflows.expired.id,
                ModelDeploymentWorkflows.project_id == PostgresConfig.project_id(),
                ModelDeploymentWorkflows.state == ModelDeploymentWorkflowState.promote_pending
            )
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
                should_train_for_promotion=True,
                id=latest_workflow.id,
                slack_training_approval_message_ts=latest_workflow.slack_training_approval_message_ts,
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
                should_train_for_promotion=True,
                id=latest_workflow.id,
                slack_training_approval_message_ts=latest_workflow.slack_training_approval_message_ts,
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

    model_deployment_workflow_for_training.id = workflow_id

    return model_deployment_workflow_for_training

@task
def update_train_pending_workflow(model_deployment_workflow_for_training: ModelDeploymentWorkflowForTraining):
    assert model_deployment_workflow_for_training.slack_training_approval_message_ts is not None

    with sql_session.begin() as session:
        session.execute(
            update(ModelDeploymentWorkflows)
            .where(
                ModelDeploymentWorkflows.id == model_deployment_workflow_for_training.id,
                ModelDeploymentWorkflows.project_id == PostgresConfig.project_id()
            )
            .values({
                ModelDeploymentWorkflows.slack_training_approval_message_ts.key: model_deployment_workflow_for_training.slack_training_approval_message_ts
            })
        )

@task
def reinitialize_train_pending_workflow(model_deployment_workflow_for_training: ModelDeploymentWorkflowForTraining | None):
    assert model_deployment_workflow_for_training is not None
    assert model_deployment_workflow_for_training.id is not None

    with sql_session.begin() as session:
        session.execute(
            update(ModelDeploymentWorkflows)
            .where(
                ModelDeploymentWorkflows.id == model_deployment_workflow_for_training.id,
                ModelDeploymentWorkflows.project_id == PostgresConfig.project_id(),
                ModelDeploymentWorkflows.state == ModelDeploymentWorkflowState.train_pending
            )
            .values({
                ModelDeploymentWorkflows.created_at.key: func.now(),
                ModelDeploymentWorkflows.state.key: ModelDeploymentWorkflowState.train_pending
            })
        )