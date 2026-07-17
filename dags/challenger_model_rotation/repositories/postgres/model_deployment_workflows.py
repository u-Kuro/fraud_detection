from airflow.sdk import task

from dags.challenger_model_rotation.modules.configs.postgres import model_deployment_workflows_config
from dags.challenger_model_rotation.repositories.mlflow.registered_model import replace_expired_model

from dags.shared.modules.configs import postgres_config
from dags.shared.modules.configs.airflow.data_keys import ModelDeploymentSuccessionKeys
from dags.shared.modules.schemas.airflow import AirflowTaskContext
from dags.shared.modules.schemas.postgres.model_deployment_workflows import ModelDeploymentWorkflowState
from dags.shared.repositories.postgres import postgres_hook
from dags.shared.services.airflow_operators import no_action

@task.branch(task_id="has_expired_promote_pending_workflow_with_replacement")
def has_expired_promote_pending_workflow_with_replacement(**context) -> str:
    results = postgres_hook.get_pandas_df(f"""
        SELECT
            expired.mlflow_run_id                   AS {ModelDeploymentSuccessionKeys.EXPIRED_MLFLOW_RUN_ID_KEY},
            expired.registered_model_name           AS {ModelDeploymentSuccessionKeys.EXPIRED_MODEL_NAME_KEY},
            expired.registered_model_version        AS {ModelDeploymentSuccessionKeys.EXPIRED_MODEL_VERSION_KEY},
            replacement.registered_model_name       AS {ModelDeploymentSuccessionKeys.REPLACEMENT_MODEL_NAME_KEY},
            replacement.registered_model_version    AS {ModelDeploymentSuccessionKeys.REPLACEMENT_MODEL_VERSION_KEY}
        FROM model_deployment_workflows expired
        JOIN model_deployment_workflows replacement
            ON replacement.project_id = %(project_id)s
            AND replacement.state = %(promote_pending_replacement_state)s
        WHERE
            expired.project_id = %(project_id)s
            AND expired.state = %(promote_pending_state)s
            AND expired.trained_at < NOW() - %(TRAINED_MODEL_EXPIRATION_DAYS)s * INTERVAL '1 day'
        LIMIT 1
        """, {
            "project_id": postgres_config.PROJECT_ID,
            "promote_pending_state": ModelDeploymentWorkflowState.promote_pending,
            "promote_pending_replacement_state": ModelDeploymentWorkflowState.promote_pending_replacement,
            "TRAINED_MODEL_EXPIRATION_DAYS": model_deployment_workflows_config.TRAINED_MODEL_EXPIRATION_DAYS,
        }
    )

    if results.empty:
        return no_action.__name__
    else:
        result = results.iloc[0]

        expired_mlflow_run_id = result[ModelDeploymentSuccessionKeys.EXPIRED_MLFLOW_RUN_ID_KEY]
        assert isinstance(expired_mlflow_run_id, str)

        expired_model_name = result[ModelDeploymentSuccessionKeys.EXPIRED_MODEL_NAME_KEY]
        assert isinstance(expired_model_name, str)

        expired_model_version = result[ModelDeploymentSuccessionKeys.EXPIRED_MODEL_VERSION_KEY]
        assert isinstance(expired_model_version, int)

        replacement_model_name = result[ModelDeploymentSuccessionKeys.REPLACEMENT_MODEL_NAME_KEY]
        assert isinstance(replacement_model_name, str)

        replacement_model_version = result[ModelDeploymentSuccessionKeys.REPLACEMENT_MODEL_VERSION_KEY]
        assert isinstance(replacement_model_version, int)

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

        return replace_expired_model.__name__