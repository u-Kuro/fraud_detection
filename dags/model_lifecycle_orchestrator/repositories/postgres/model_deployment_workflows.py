from uuid import UUID

from airflow.sdk import task

from dags.model_lifecycle_orchestrator.controllers.slack import invalidate_old_training_approval
from dags.model_lifecycle_orchestrator.modules.configs.postgres.model_deployment_workflows import ModelDeploymentWorkflowsConfig
from dags.model_lifecycle_orchestrator.modules.schemas.airflow.branches import DispatchTrainingApprovalBranches
from dags.model_lifecycle_orchestrator.modules.schemas.airflow.xcom import DeleteExpiredPromotePendingWorkflowXCom, CheckCurrentModelDeploymentWorkflowDriftedXCom
from dags.model_lifecycle_orchestrator.modules.schemas.model_deployment_workflows import ModelDeploymentWorkflow
from dags.model_lifecycle_orchestrator.repositories.mlflow.registered_model import replace_expired_model
from dags.shared.modules.configs.airflow.data_keys import ModelDeploymentSuccessionKeys, ModelDeploymentWorkflowsKeys
from dags.shared.modules.configs.postgres import PostgresConfig
from dags.shared.modules.schemas.airflow import AirflowTaskContext
from dags.shared.modules.schemas.postgres.model_deployment_workflows import ModelDeploymentWorkflowState
from dags.shared.repositories.postgres import postgres_hook
from dags.shared.services.airflow_operators import no_action


@task.branch(task_id="has_expired_promote_pending_workflow_with_replacement")
def has_expired_promote_pending_workflow_with_replacement(**context) -> str:
    results = postgres_hook.get_pandas_df(f"""
        SELECT
            replacement.registered_model_name       AS {ModelDeploymentSuccessionKeys.REPLACEMENT_MODEL_NAME},
            replacement.registered_model_version    AS {ModelDeploymentSuccessionKeys.REPLACEMENT_MODEL_VERSION},
            
            expired.registered_model_name           AS {ModelDeploymentSuccessionKeys.EXPIRED_MODEL_NAME},
            expired.registered_model_version        AS {ModelDeploymentSuccessionKeys.EXPIRED_MODEL_VERSION},
                        
            expired.mlflow_run_id                   AS {ModelDeploymentSuccessionKeys.EXPIRED_MLFLOW_RUN_ID},
            
            expired.id                              AS {ModelDeploymentSuccessionKeys.EXPIRED_ID}
        FROM model_deployment_workflows expired
        JOIN model_deployment_workflows replacement
            ON replacement.project_id = %(project_id)s
            AND replacement.state = %(promote_pending_replacement_state)s
        WHERE
            expired.project_id = %(project_id)s
            AND expired.state = %(promote_pending_state)s
            AND expired.trained_at < NOW() - %(trained_model_expiration_days)s * INTERVAL '1 day'
        LIMIT 1
        """, {
            "project_id": PostgresConfig.PROJECT_ID,
            "promote_pending_state": ModelDeploymentWorkflowState.promote_pending,
            "promote_pending_replacement_state": ModelDeploymentWorkflowState.promote_pending_replacement,
            "trained_model_expiration_days": ModelDeploymentWorkflowsConfig.trained_model_expiration_days,
        }
    )

    if results.empty:
        return no_action.__name__
    else:
        result = results.iloc[0]

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

        return replace_expired_model.__name__

@task(task_id="delete_expired_promote_pending_workflow")
def delete_expired_promote_pending_workflow(**context) -> None:
    delete_expired_promote_pending_workflow_xcom = DeleteExpiredPromotePendingWorkflowXCom.from_context(context)

    postgres_hook.run("""
        DELETE FROM model_deployment_workflows
        WHERE 
            id = %(id)s
            AND project_id = %(project_id)s
            AND state = %(state)s
        """, parameters={
            "id": delete_expired_promote_pending_workflow_xcom.expired_id,
            "project_id": PostgresConfig.PROJECT_ID,
            "state": ModelDeploymentWorkflowState.promote_pending,
        }
    )

def get_current_model_deployment_workflows() -> list[ModelDeploymentWorkflow] | None:
    model_deployment_workflow_keys = ModelDeploymentWorkflow.model_field_keys()
    model_deployment_workflow_rows = postgres_hook.get_records(f"""
        SELECT {",".join(model_deployment_workflow_keys)}
        FROM model_deployment_workflows
        WHERE project_id = %(project_id)s
        ORDER BY created_at DESC
        LIMIT 2
        """, {
            "project_id": PostgresConfig.PROJECT_ID
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
    result = postgres_hook.get_first("""
        INSERT INTO model_deployment_workflows (
            project_id,
            state
        )
        VALUES (
            %(project_id)s,
            %(state)s
        )
        RETURNING id
        """, parameters={
            "project_id": PostgresConfig.PROJECT_ID,
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
    postgres_hook.run("""
        UPDATE model_deployment_workflows
        SET created_at = NOW(),
            state = %(state)s
        WHERE
            id = %(id)s
        AND project_id = %(project_id)s
        """, parameters={
            "id": workflow_id,
            "project_id": PostgresConfig.PROJECT_ID,
            "state": ModelDeploymentWorkflowState.train_pending
        }
    )

@task(task_id="update_train_pending_workflow")
def update_train_pending_workflow(**context) -> None:
    postgres_hook.run("""
        UPDATE model_deployment_workflows
        SET training_approval_slack_ts = %(training_approval_slack_ts)s
        WHERE
            id = %(id)s
        AND project_id = %(project_id)s
        """, parameters={
            "id": workflow_id,
            "project_id": PostgresConfig.PROJECT_ID,
            "training_approval_slack_ts": training_approval_slack_ts
        }
    )

@task.branch(task_id="check_current_model_deployment_workflows")
def check_current_model_deployment_workflows(branch: DispatchTrainingApprovalBranches, **context) -> str:
    current_model_deployment_workflows = get_current_model_deployment_workflows()
    if branch == DispatchTrainingApprovalBranches.drifted:
        check_current_model_deployment_workflow_xcom = CheckCurrentModelDeploymentWorkflowDriftedXCom.from_context(context)
    else:
        pass
    ti = AirflowTaskContext.from_context(context).ti

    if current_model_deployment_workflows is None:
        # post
        return initialize_train_pending_workflow.__name__
    elif len(current_model_deployment_workflows) == 1:
        latest_workflow = current_model_deployment_workflows.pop()
        if latest_workflow.state == ModelDeploymentWorkflowState.train_pending:
            # replace
            ti.xcom_push(
                key=ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID,
                value=str(latest_workflow.id),
            )
            ti.xcom_push(
                key=ModelDeploymentWorkflowsKeys.TRAINING_APPROVAL_SLACK_TS,
                value=str(latest_workflow.training_approval_slack_ts),
            )
            return invalidate_old_training_approval.__name__
        elif latest_workflow.state == ModelDeploymentWorkflowState.promote_pending:
            # post
            return initialize_train_pending_workflow.__name__
        else:
            raise ValueError(f"Unexpected workflow state with 1 active workflow: {latest_workflow.state!r}")
    else:
        last_workflow = current_model_deployment_workflows.pop()
        if last_workflow.state != ModelDeploymentWorkflowState.promote_pending:
            raise ValueError(f"Expected latest workflow state to be promote_pending, got: {last_workflow.state!r}")

        latest_workflow = current_model_deployment_workflows.pop()
        if latest_workflow.state == ModelDeploymentWorkflowState.train_pending:
            # replace
            ti.xcom_push(
                key=ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID,
                value=str(latest_workflow.id),
            )
            ti.xcom_push(
                key=ModelDeploymentWorkflowsKeys.TRAINING_APPROVAL_SLACK_TS,
                value=str(latest_workflow.training_approval_slack_ts),
            )
            return invalidate_old_training_approval.__name__
        elif latest_workflow.state == ModelDeploymentWorkflowState.promote_pending_replacement:
            return no_action.__name__
        else:
            raise ValueError(f"Unexpected workflow state with 2 active workflows: {latest_workflow.state!r}")