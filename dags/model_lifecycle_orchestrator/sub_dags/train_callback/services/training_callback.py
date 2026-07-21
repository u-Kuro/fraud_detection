from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sdk import task

from dags.model_lifecycle_orchestrator.sub_dags.train_callback.modules.schemas.airflow.configurations import TrainingCallbackConfigurations

from dags.shared.modules.configs.airflow import ModelDeploymentWorkflowsKeys
from dags.shared.modules.schemas.airflow import AirflowTaskContext
from dags.model_lifecycle_orchestrator.sub_dags.train_callback.modules.schemas.airflow.xcom import StartTrainingPipelineXCom
from dags.model_lifecycle_orchestrator.sub_dags.train_callback.repositories.model_deployment_workflows import update_approved_training_workflow, delete_rejected_training_workflow

training_callback_task_id = "training_callback"
@task.branch(task_id=training_callback_task_id)
def training_callback(**context) -> str:
    configurations = TrainingCallbackConfigurations.from_context(context)

    ti = AirflowTaskContext.from_context(context).ti
    ti.xcom_push(
        key=ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID,
        value=str(configurations.workflow_id)
    )

    if configurations.approved:
        return update_approved_training_workflow.__name__
    else:
        return delete_rejected_training_workflow.__name__

def start_training_pipeline(**context) -> TriggerDagRunOperator:
    configurations = StartTrainingPipelineXCom.from_context(context)

    return TriggerDagRunOperator(
        task_id=start_training_pipeline.__name__,
        trigger_dag_id="training_pipeline",
        wait_for_completion=False,
        conf={
            ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID: configurations.workflow_id
        }
    )