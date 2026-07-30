from uuid import UUID

from airflow.sdk import task, get_current_context
from sqlalchemy import select, func, true, literal, cast, delete, insert, update
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.orm import aliased

from dags.model_lifecycle_orchestrator.check_training_need.controllers.slack import invalidate_old_training_approval, invalidate_expired_promotion_approval
from dags.model_lifecycle_orchestrator.check_training_need.modules.configs.airflow.data_keys import ModelDeploymentSuccessionKeys
from dags.model_lifecycle_orchestrator.check_training_need.modules.configs.postgres.model_deployment_workflows import ModelDeploymentWorkflowsConfig
from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.airflow.branches import NoActionBranches
from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.airflow.xcom import DeleteExpiredPromotePendingWorkflowXCom, ReinitializeTrainPendingWorkflow, UpdateTrainPendingWorkflow
from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.model_deployment_workflows import ModelDeploymentWorkflow
from dags.model_lifecycle_orchestrator.check_training_need.services.tasks import invalidate_expired_challenger_model, no_action
from dags.shared.modules.configs.airflow.data_keys import ModelDeploymentWorkflowsKeys
from dags.shared.modules.configs.postgres import PostgresConfig
from dags.shared.modules.schemas.airflow import AirflowTaskContext
from dags.shared.modules.schemas.postgres.model_deployment_workflows import ModelDeploymentWorkflows, ModelDeploymentWorkflowState
from dags.shared.modules.utilities.airflow.xcom import build_task_id
from dags.shared.modules.utilities.postgres.sqlalchemy import field
from dags.shared.repositories.postgres.postgres import sql_session

@task.branch(task_id="has_expired_promote_pending_workflow_with_replacement")
def has_expired_promote_pending_workflow_with_replacement() -> str:
    context = get_current_context()

    with sql_session.begin() as session:
        expired_model_deployment_workflow = aliased(
            ModelDeploymentWorkflows,
            select(ModelDeploymentWorkflows)
            .where(
                ModelDeploymentWorkflows.project_id == PostgresConfig.PROJECT_ID(),
                ModelDeploymentWorkflows.state == ModelDeploymentWorkflowState.promote_pending,
                ModelDeploymentWorkflows.model_trained_at <= func.now() - (
                    literal(ModelDeploymentWorkflowsConfig.challenger_model_expiration_days)
                    * cast(literal("1 day"), INTERVAL)
                )
            )
            .subquery(name="expired_model_deployment_workflow")
        )
        replacement_model_deployment_workflow = aliased(
            ModelDeploymentWorkflows,
            select(ModelDeploymentWorkflows)
            .where(
                ModelDeploymentWorkflows.project_id == PostgresConfig.PROJECT_ID(),
                ModelDeploymentWorkflows.state == ModelDeploymentWorkflowState.promote_pending_replacement
            )
            .subquery(name="replacement_model_deployment_workflow")
        )

        result = session.execute(
            select(
                field(expired_model_deployment_workflow.promotion_approval_slack_ts)
                .label(ModelDeploymentSuccessionKeys.EXPIRED_PROMOTION_APPROVAL_SLACK_TS),

                field(replacement_model_deployment_workflow.registered_model_name)
                .label(ModelDeploymentSuccessionKeys.REPLACEMENT_MODEL_NAME),
                field(replacement_model_deployment_workflow.registered_model_version)
                .label(ModelDeploymentSuccessionKeys.REPLACEMENT_MODEL_VERSION),

                field(expired_model_deployment_workflow.registered_model_name)
                .label(ModelDeploymentSuccessionKeys.EXPIRED_MODEL_NAME),
                field(expired_model_deployment_workflow.registered_model_version)
                .label(ModelDeploymentSuccessionKeys.EXPIRED_MODEL_VERSION),

                field(expired_model_deployment_workflow.mlflow_run_id)
                .label(ModelDeploymentSuccessionKeys.EXPIRED_MLFLOW_RUN_ID),

                field(expired_model_deployment_workflow.id)
                .label(ModelDeploymentSuccessionKeys.EXPIRED_ID)
            ).join_from(
                expired_model_deployment_workflow,
                replacement_model_deployment_workflow,
                onclause=true()
            )
            .limit(1)
        ).mappings().first()

    if result is None:
        return build_task_id((
            invalidate_expired_challenger_model.__name__,
            no_action.__name__,
            NoActionBranches.no_expired_promote_pending_workflow_with_replacement
        ))
    else:
        expired_promotion_approval_slack_ts = result[ModelDeploymentSuccessionKeys.EXPIRED_PROMOTION_APPROVAL_SLACK_TS]
        assert isinstance(expired_promotion_approval_slack_ts, str)

        replacement_model_name = result[ModelDeploymentSuccessionKeys.REPLACEMENT_MODEL_NAME]
        assert isinstance(replacement_model_name, str)

        replacement_model_version = result[ModelDeploymentSuccessionKeys.REPLACEMENT_MODEL_VERSION]
        assert isinstance(replacement_model_version, int)

        expired_model_name = result[ModelDeploymentSuccessionKeys.EXPIRED_MODEL_NAME]
        assert isinstance(expired_model_name, str)

        expired_model_version = result[ModelDeploymentSuccessionKeys.EXPIRED_MODEL_VERSION]
        assert isinstance(expired_model_version, int)

        expired_mlflow_run_id = result[ModelDeploymentSuccessionKeys.EXPIRED_MLFLOW_RUN_ID]
        assert isinstance(expired_mlflow_run_id, str)

        expired_id = result[ModelDeploymentSuccessionKeys.EXPIRED_ID]
        assert isinstance(expired_id, UUID)

        ti = AirflowTaskContext.from_context(context).ti
        ti.xcom_push(
            key=ModelDeploymentSuccessionKeys.EXPIRED_PROMOTION_APPROVAL_SLACK_TS,
            value=expired_promotion_approval_slack_ts
        )

        ti.xcom_push(
            key=ModelDeploymentSuccessionKeys.REPLACEMENT_MODEL_NAME,
            value=replacement_model_name
        )
        ti.xcom_push(
            key=ModelDeploymentSuccessionKeys.REPLACEMENT_MODEL_VERSION,
            value=replacement_model_version
        )

        ti.xcom_push(
            key=ModelDeploymentSuccessionKeys.EXPIRED_MODEL_NAME,
            value=expired_model_name
        )
        ti.xcom_push(
            key=ModelDeploymentSuccessionKeys.EXPIRED_MODEL_VERSION,
            value=expired_model_version
        )

        ti.xcom_push(
            key=ModelDeploymentSuccessionKeys.EXPIRED_MLFLOW_RUN_ID,
            value=expired_mlflow_run_id
        )

        ti.xcom_push(
            key=ModelDeploymentSuccessionKeys.EXPIRED_ID,
            value=str(expired_id)
        )

        return build_task_id((
            invalidate_expired_challenger_model.__name__,
            invalidate_expired_promotion_approval.__name__
        ))

@task(task_id="delete_expired_promote_pending_workflow")
def delete_expired_promote_pending_workflow() -> None:
    context = get_current_context()

    delete_expired_promote_pending_workflow_xcom = DeleteExpiredPromotePendingWorkflowXCom.from_context(context)

    with sql_session.begin() as session:
        session.execute(
            delete(ModelDeploymentWorkflows)
            .where(
                ModelDeploymentWorkflows.id == delete_expired_promote_pending_workflow_xcom.expired_id,
                ModelDeploymentWorkflows.project_id == PostgresConfig.PROJECT_ID(),
                ModelDeploymentWorkflows.state == ModelDeploymentWorkflowState.promote_pending
            )
        )

@task(task_id="initialize_train_pending_workflow")
def initialize_train_pending_workflow() -> None:
    context = get_current_context()

    with sql_session.begin() as session:
        (workflow_id,) = session.execute(
            insert(ModelDeploymentWorkflows)
            .values({
                ModelDeploymentWorkflows.project_id.key: PostgresConfig.PROJECT_ID(),
                ModelDeploymentWorkflows.state.key: ModelDeploymentWorkflowState.train_pending
            })
            .returning(
                ModelDeploymentWorkflows.id
            )
        ).one().t

    ti = AirflowTaskContext.from_context(context).ti
    ti.xcom_push(
        key=ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID,
        value=str(workflow_id),
    )

@task(task_id="reinitialize_train_pending_workflow")
def reinitialize_train_pending_workflow() -> None:
    context = get_current_context()

    reinitialize_train_pending_workflow_xcom = ReinitializeTrainPendingWorkflow.from_context(context)

    with sql_session.begin() as session:
        session.execute(
            update(ModelDeploymentWorkflows)
            .where(
                ModelDeploymentWorkflows.id == reinitialize_train_pending_workflow_xcom.workflow_id,
                ModelDeploymentWorkflows.project_id == PostgresConfig.PROJECT_ID(),
                ModelDeploymentWorkflows.state == ModelDeploymentWorkflowState.train_pending
            )
            .values({
                ModelDeploymentWorkflows.created_at.key: func.now(),
                ModelDeploymentWorkflows.state.key: ModelDeploymentWorkflowState.train_pending
            })
        )

@task(task_id="update_train_pending_workflow")
def update_train_pending_workflow() -> None:
    context = get_current_context()

    update_train_pending_workflow_xcom = UpdateTrainPendingWorkflow.from_context(context)

    with sql_session.begin() as session:
        session.execute(
            update(ModelDeploymentWorkflows)
            .where(
                ModelDeploymentWorkflows.id == update_train_pending_workflow_xcom.workflow_id,
                ModelDeploymentWorkflows.project_id == PostgresConfig.PROJECT_ID()
            )
            .values({
                ModelDeploymentWorkflows.training_approval_slack_ts.key: update_train_pending_workflow_xcom.training_approval_slack_ts
            })
        )

@task.branch(task_id="check_current_model_deployment_workflows")
def check_current_model_deployment_workflows() -> str:
    context = get_current_context()

    ti = AirflowTaskContext.from_context(context).ti

    with sql_session.begin() as session:
        model_deployment_workflow_rows = session.execute(
            select(ModelDeploymentWorkflows)
            .where(
                ModelDeploymentWorkflows.project_id == PostgresConfig.PROJECT_ID()
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
        ti.xcom_push(
            key=ModelDeploymentWorkflowsKeys.TRAIN_MODEL_FOR_PROMOTION,
            value=True,
        )
        return initialize_train_pending_workflow.__name__
    elif current_model_deployment_workflows_length == 1:
        latest_workflow = current_model_deployment_workflows.pop()
        if latest_workflow.state == ModelDeploymentWorkflowState.train_pending:
            ti.xcom_push(
                key=ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID,
                value=str(latest_workflow.id),
            )
            ti.xcom_push(
                key=ModelDeploymentWorkflowsKeys.TRAINING_APPROVAL_SLACK_TS,
                value=latest_workflow.training_approval_slack_ts,
            )
            ti.xcom_push(
                key=ModelDeploymentWorkflowsKeys.TRAIN_MODEL_FOR_PROMOTION,
                value=True,
            )
            return invalidate_old_training_approval.__name__
        elif latest_workflow.state == ModelDeploymentWorkflowState.promote_pending:
            ti.xcom_push(
                key=ModelDeploymentWorkflowsKeys.TRAIN_MODEL_FOR_PROMOTION,
                value=False,
            )
            return initialize_train_pending_workflow.__name__
        else:
            raise ValueError(f"Unexpected workflow state with 1 active workflow: {latest_workflow.state!r}")
    elif current_model_deployment_workflows_length == 2:
        last_workflow = current_model_deployment_workflows.pop()
        if last_workflow.state != ModelDeploymentWorkflowState.promote_pending:
            raise ValueError(f"Expected latest workflow state to be promote_pending, got: {last_workflow.state!r}")

        latest_workflow = current_model_deployment_workflows.pop()
        if latest_workflow.state == ModelDeploymentWorkflowState.train_pending:
            ti.xcom_push(
                key=ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID,
                value=str(latest_workflow.id),
            )
            ti.xcom_push(
                key=ModelDeploymentWorkflowsKeys.TRAINING_APPROVAL_SLACK_TS,
                value=latest_workflow.training_approval_slack_ts,
            )
            ti.xcom_push(
                key=ModelDeploymentWorkflowsKeys.TRAIN_MODEL_FOR_PROMOTION,
                value=True,
            )
            return invalidate_old_training_approval.__name__
        elif latest_workflow.state == ModelDeploymentWorkflowState.promote_pending_replacement:
            return no_action.__name__
        else:
            raise ValueError(f"Unexpected workflow state with 2 active workflows: {latest_workflow.state!r}")
    else:
        raise ValueError(f"Unexpected number of active workflows: {current_model_deployment_workflows_length}")