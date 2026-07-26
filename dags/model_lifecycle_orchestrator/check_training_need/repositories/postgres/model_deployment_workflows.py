from uuid import UUID

from airflow.sdk import task

from dags.model_lifecycle_orchestrator.check_training_need.controllers.slack import invalidate_old_training_approval
from dags.model_lifecycle_orchestrator.check_training_need.modules.configs.airflow.data_keys import ModelDeploymentSuccessionKeys
from dags.model_lifecycle_orchestrator.check_training_need.modules.configs.postgres.model_deployment_workflows import ModelDeploymentWorkflowsConfig
from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.airflow.branches import NoActionBranches
from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.airflow.xcom import DeleteExpiredPromotePendingWorkflowXCom, ReinitializeTrainPendingWorkflow, UpdateTrainPendingWorkflow
from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.model_deployment_workflows import ModelDeploymentWorkflow
from dags.model_lifecycle_orchestrator.check_training_need.services.tasks import invalidate_expired_challenger_model, no_action
from dags.shared.modules.configs.airflow.data_keys import ModelDeploymentWorkflowsKeys
from dags.shared.modules.configs.postgres import PostgresConfig
from dags.shared.modules.schemas.airflow import AirflowTaskContext
from dags.shared.modules.schemas.postgres.model_deployment_workflows import ModelDeploymentWorkflowState, ModelDeploymentWorkflowsColumnKeys
from dags.shared.modules.schemas.postgres.postgres import PostgresTableKeys
from dags.shared.modules.utilities.airflow.xcom import build_task_id
from dags.shared.repositories.postgres import postgres_hook

@task.branch(task_id="has_expired_promote_pending_workflow_with_replacement")
def has_expired_promote_pending_workflow_with_replacement(**context) -> str:
    results = postgres_hook.get_pandas_df(f"""
        SELECT
            expired.{ModelDeploymentWorkflowsColumnKeys.promotion_approval_slack_ts}
                 AS {ModelDeploymentSuccessionKeys.EXPIRED_PROMOTION_APPROVAL_SLACK_TS},
                 
            replacement.{ModelDeploymentWorkflowsColumnKeys.registered_model_name}
                 AS {ModelDeploymentSuccessionKeys.REPLACEMENT_MODEL_NAME},
            replacement.{ModelDeploymentWorkflowsColumnKeys.registered_model_version}
                 AS {ModelDeploymentSuccessionKeys.REPLACEMENT_MODEL_VERSION},
            
            expired.{ModelDeploymentWorkflowsColumnKeys.registered_model_name}
                 AS {ModelDeploymentSuccessionKeys.EXPIRED_MODEL_NAME},
            expired.{ModelDeploymentWorkflowsColumnKeys.registered_model_version}
                 AS {ModelDeploymentSuccessionKeys.EXPIRED_MODEL_VERSION},
                        
            expired.{ModelDeploymentWorkflowsColumnKeys.mlflow_run_id}
                 AS {ModelDeploymentSuccessionKeys.EXPIRED_MLFLOW_RUN_ID},
            
            expired.{ModelDeploymentWorkflowsColumnKeys.id}
                  AS {ModelDeploymentSuccessionKeys.EXPIRED_ID}
        FROM {PostgresTableKeys.model_deployment_workflows} expired
        JOIN {PostgresTableKeys.model_deployment_workflows} replacement
            ON replacement.{ModelDeploymentWorkflowsColumnKeys.project_id} = %(project_id)s
            AND replacement.{ModelDeploymentWorkflowsColumnKeys.state} = %(promote_pending_replacement_state)s
        WHERE
            expired.{ModelDeploymentWorkflowsColumnKeys.project_id} = %(project_id)s
        AND expired.{ModelDeploymentWorkflowsColumnKeys.state} = %(promote_pending_state)s
        AND expired.{ModelDeploymentWorkflowsColumnKeys.model_trained_at} < NOW() - %(challenger_model_expiration_days)s * INTERVAL '1 day'
        LIMIT 1
        """, {
            "project_id": PostgresConfig.PROJECT_ID(),
            "promote_pending_state": ModelDeploymentWorkflowState.promote_pending,
            "promote_pending_replacement_state": ModelDeploymentWorkflowState.promote_pending_replacement,
            "challenger_model_expiration_days": ModelDeploymentWorkflowsConfig.challenger_model_expiration_days,
        }
    )

    if results.empty:
        return build_task_id((
            invalidate_expired_challenger_model.__name__,
            no_action.__name__,
            NoActionBranches.no_expired_promote_pending_workflow_with_replacement
        ))
    else:
        result = results.iloc[0]

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
            invalidate_slack_promotion_approval.__name__
        ))

@task(task_id="delete_expired_promote_pending_workflow")
def delete_expired_promote_pending_workflow(**context) -> None:
    delete_expired_promote_pending_workflow_xcom = DeleteExpiredPromotePendingWorkflowXCom.from_context(context)

    postgres_hook.run(f"""
        DELETE FROM {PostgresTableKeys.model_deployment_workflows}
        WHERE 
            {ModelDeploymentWorkflowsColumnKeys.id} = %(id)s
        AND {ModelDeploymentWorkflowsColumnKeys.project_id} = %(project_id)s
        AND {ModelDeploymentWorkflowsColumnKeys.state} = %(state)s
        """, parameters={
            "id": delete_expired_promote_pending_workflow_xcom.expired_id,
            "project_id": PostgresConfig.PROJECT_ID(),
            "state": ModelDeploymentWorkflowState.promote_pending,
        }
    )

def get_current_model_deployment_workflows() -> list[ModelDeploymentWorkflow] | None:
    model_deployment_workflow_keys = ModelDeploymentWorkflow.model_field_keys()
    model_deployment_workflow_rows = postgres_hook.get_records(f"""
        SELECT {",".join(model_deployment_workflow_keys)}
        FROM {PostgresTableKeys.model_deployment_workflows}
        WHERE {ModelDeploymentWorkflowsColumnKeys.project_id} = %(project_id)s
        ORDER BY {ModelDeploymentWorkflowsColumnKeys.created_at} DESC
        LIMIT 2
        """, {
            "project_id": PostgresConfig.PROJECT_ID()
        }
    )

    if len(model_deployment_workflow_rows) == 0:
        return None
    else:
        return [
            ModelDeploymentWorkflow.model_validate(
                dict(zip(model_deployment_workflow_keys, row)),
                from_attributes=True
            )
            for row in model_deployment_workflow_rows
        ]

@task(task_id="initialize_train_pending_workflow")
def initialize_train_pending_workflow(**context) -> None:
    result = postgres_hook.get_first(f"""
        INSERT INTO {PostgresTableKeys.model_deployment_workflows} (
            {ModelDeploymentWorkflowsColumnKeys.project_id},
            {ModelDeploymentWorkflowsColumnKeys.state}
        )
        VALUES (
            %(project_id)s,
            %(state)s
        )
        RETURNING {ModelDeploymentWorkflowsColumnKeys.id}
        """, parameters={
            "project_id": PostgresConfig.PROJECT_ID(),
            "state": ModelDeploymentWorkflowState.train_pending
        }
    )

    workflow_id: UUID = result[0]

    assert isinstance(workflow_id, UUID)

    ti = AirflowTaskContext.from_context(context).ti
    ti.xcom_push(
        key=ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID,
        value=str(workflow_id),
    )

@task(task_id="reinitialize_train_pending_workflow")
def reinitialize_train_pending_workflow(**context) -> None:
    reinitialize_train_pending_workflow_xcom = ReinitializeTrainPendingWorkflow.from_context(context)

    postgres_hook.run(f"""
        UPDATE {PostgresTableKeys.model_deployment_workflows}
        SET {ModelDeploymentWorkflowsColumnKeys.created_at} = NOW(),
            {ModelDeploymentWorkflowsColumnKeys.state} = %(state)s
        WHERE
            {ModelDeploymentWorkflowsColumnKeys.id} = %(id)s
        AND {ModelDeploymentWorkflowsColumnKeys.project_id} = %(project_id)s
        """, parameters={
            "id": reinitialize_train_pending_workflow_xcom.workflow_id,
            "project_id": PostgresConfig.PROJECT_ID(),
            "state": ModelDeploymentWorkflowState.train_pending
        }
    )

@task(task_id="update_train_pending_workflow")
def update_train_pending_workflow(**context) -> None:
    update_train_pending_workflow_xcom = UpdateTrainPendingWorkflow.from_context(context)

    postgres_hook.run(f"""
        UPDATE {PostgresTableKeys.model_deployment_workflows}
        SET {ModelDeploymentWorkflowsColumnKeys.training_approval_slack_ts} = %(training_approval_slack_ts)s
        WHERE
            {ModelDeploymentWorkflowsColumnKeys.id} = %(id)s
        AND {ModelDeploymentWorkflowsColumnKeys.project_id} = %(project_id)s
        """, parameters={
            "id": update_train_pending_workflow_xcom.workflow_id,
            "project_id": PostgresConfig.PROJECT_ID(),
            "training_approval_slack_ts": update_train_pending_workflow_xcom.training_approval_slack_ts
        }
    )

@task.branch(task_id="check_current_model_deployment_workflows")
def check_current_model_deployment_workflows(**context) -> str:
    ti = AirflowTaskContext.from_context(context).ti

    current_model_deployment_workflows = get_current_model_deployment_workflows()

    if current_model_deployment_workflows is None:
        ti.xcom_push(
            key=ModelDeploymentWorkflowsKeys.TRAIN_MODEL_FOR_PROMOTION,
            value=True,
        )
        return initialize_train_pending_workflow.__name__
    elif len(current_model_deployment_workflows) == 1:
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
    else:
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