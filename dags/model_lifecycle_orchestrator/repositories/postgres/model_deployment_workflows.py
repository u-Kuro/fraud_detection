from uuid import UUID

from airflow.sdk import task

from dags.model_lifecycle_orchestrator.modules.configs.postgres.model_deployment_workflows import ModelDeploymentWorkflowsConfig
from dags.model_lifecycle_orchestrator.modules.schemas.airflow.xcom import DeleteExpiredPromotePendingWorkflowXCom
from dags.model_lifecycle_orchestrator.repositories.mlflow.registered_model import replace_expired_model
from dags.shared.modules.configs.airflow.data_keys import ModelDeploymentSuccessionKeys
from dags.shared.modules.configs.postgres import PostgresConfig
from dags.shared.modules.schemas.airflow import AirflowTaskContext
from dags.shared.modules.schemas.postgres.model_deployment_workflows import ModelDeploymentWorkflowState
from dags.shared.repositories.postgres import postgres_hook
from dags.shared.services.airflow_operators import no_action


@task.branch(task_id="has_expired_promote_pending_workflow_with_replacement")
def has_expired_promote_pending_workflow_with_replacement(**context) -> str:
    results = postgres_hook.get_pandas_df(f"""
        SELECT
            replacement.registered_model_name       AS {ModelDeploymentSuccessionKeys.REPLACEMENT_MODEL_NAME_KEY},
            replacement.registered_model_version    AS {ModelDeploymentSuccessionKeys.REPLACEMENT_MODEL_VERSION_KEY},
            
            expired.registered_model_name           AS {ModelDeploymentSuccessionKeys.EXPIRED_MODEL_NAME_KEY},
            expired.registered_model_version        AS {ModelDeploymentSuccessionKeys.EXPIRED_MODEL_VERSION_KEY},
                        
            expired.mlflow_run_id                   AS {ModelDeploymentSuccessionKeys.EXPIRED_MLFLOW_RUN_ID_KEY},
            
            expired.id                              AS {ModelDeploymentSuccessionKeys.EXPIRED_ID_KEY}
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

        replacement_model_name = result[ModelDeploymentSuccessionKeys.REPLACEMENT_MODEL_NAME_KEY]
        assert isinstance(replacement_model_name, str)

        replacement_model_version = result[ModelDeploymentSuccessionKeys.REPLACEMENT_MODEL_VERSION_KEY]
        assert isinstance(replacement_model_version, int)

        expired_model_name = result[ModelDeploymentSuccessionKeys.EXPIRED_MODEL_NAME_KEY]
        assert isinstance(expired_model_name, str)

        expired_model_version = result[ModelDeploymentSuccessionKeys.EXPIRED_MODEL_VERSION_KEY]
        assert isinstance(expired_model_version, int)

        expired_mlflow_run_id = result[ModelDeploymentSuccessionKeys.EXPIRED_MLFLOW_RUN_ID_KEY]
        assert isinstance(expired_mlflow_run_id, str)

        expired_id = result[ModelDeploymentSuccessionKeys.EXPIRED_ID_KEY]
        assert isinstance(expired_id, UUID)

        ti = AirflowTaskContext.from_context(context).ti
        ti.xcom_push(
            key=ModelDeploymentSuccessionKeys.REPLACEMENT_MODEL_NAME_KEY,
            value=replacement_model_name
        )
        ti.xcom_push(
            key=ModelDeploymentSuccessionKeys.REPLACEMENT_MODEL_VERSION_KEY,
            value=replacement_model_version
        )

        ti.xcom_push(
            key=ModelDeploymentSuccessionKeys.EXPIRED_MODEL_NAME_KEY,
            value=expired_model_name
        )
        ti.xcom_push(
            key=ModelDeploymentSuccessionKeys.EXPIRED_MODEL_VERSION_KEY,
            value=expired_model_version
        )

        ti.xcom_push(
            key=ModelDeploymentSuccessionKeys.EXPIRED_MLFLOW_RUN_ID_KEY,
            value=expired_mlflow_run_id
        )

        ti.xcom_push(
            key=ModelDeploymentSuccessionKeys.EXPIRED_ID_KEY,
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
    # TODO - 19/07/2026 Need to align with new stuff/branch in task group
    check_current_model_deployment_workflow_xcom = CheckCurrentModelDeploymentWorkflowXCom.from_context(context)

    current_model_deployment_workflow = get_current_model_deployment_workflow()

    if current_model_deployment_workflow is None:
        branch = post_training_approval.__name__
    elif current_model_deployment_workflow.state == ModelDeploymentWorkflowState.train_pending:
        branch = update_training_approval.__name__
    else:
        branch = no_action.__name__

    if branch != no_action.__name__:
        ti = AirflowTaskContext.from_context(context).ti
        ti.xcom_push(
            key=DriftMonitorKeys.DRIFT_SUMMARY_KEY,
            value=check_current_model_deployment_workflow_xcom.drift_summary,
        )
        if branch == update_training_approval.__name__:
            assert isinstance(current_model_deployment_workflow, ModelDeploymentWorkflows)
            ti.xcom_push(
                key=ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID_KEY,
                value=str(current_model_deployment_workflow.id),
            )
            ti.xcom_push(
                key=ModelDeploymentWorkflowsKeys.TRAINING_APPROVAL_SLACK_TS_KEY,
                value=current_model_deployment_workflow.training_approval_slack_ts,
            )

    return branch