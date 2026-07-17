from airflow.sdk import task

from dags.model_lifecycle_monitor.controllers.slack import post_training_approval, update_training_approval

from dags.model_lifecycle_monitor.modules.schemas.airflow.xcom import CheckCurrentModelDeploymentWorkflowXCom
from dags.model_lifecycle_monitor.modules.schemas.model_deployment_workflows import ModelDeploymentWorkflows, ModelDeploymentWorkflowState

from dags.shared.modules.configs import postgres_config
from dags.shared.modules.configs.airflow import ModelDeploymentWorkflowsKeys, DriftMonitorKeys
from dags.shared.modules.schemas.airflow import AirflowTaskContext
from dags.shared.repositories.postgres import postgres_hook
from dags.shared.services.airflow_operators import no_action

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