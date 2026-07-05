from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sdk import task

from dags.modules.configs.dags import dags_config
from dags.modules.schemas.airflow import TrainCallbackConfigurations, AirflowTaskContext
from dags.repositories.postgres.model_deployment_workflows import training_approved, training_rejected
from dags.services.airflow_operators import no_action

train_callback_task_id = "train_callback"
@task.branch(task_id=train_callback_task_id)
def train_callback(**context) -> str:
    configurations = TrainCallbackConfigurations.from_context(context)
    if configurations.approved:
        task_context = AirflowTaskContext.from_context(context)
        # TODO - try and check if PostgresHook() is more used. but it needs environment variable to connect so im doubting to check first
        training_approved(configurations.workflow_id)
        task_context.ti.xcom_push(
            key=dags_config.MODEL_DEPLOYMENT_WORKFLOW_ID,
            value=str(configurations.workflow_id)
        )
        return start_training_pipeline.__name__
    else:
        training_rejected(configurations.workflow_id)
        return no_action.__name__

def start_training_pipeline(**context) -> TriggerDagRunOperator:
    task_context = AirflowTaskContext.from_context(context)
    model_deployment_workflow_id = task_context.ti.xcom_pull(
        task_ids=train_callback_task_id,
        key=dags_config.MODEL_DEPLOYMENT_WORKFLOW_ID
    )
    return TriggerDagRunOperator(
        task_id=start_training_pipeline.__name__,
        trigger_dag_id="training_pipeline",
        wait_for_completion=False,
        conf={
            dags_config.MODEL_DEPLOYMENT_WORKFLOW_ID: model_deployment_workflow_id
        }
    )