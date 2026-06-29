from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sdk import task

from dags.modules.schemas.configurations import TrainCallbackConfigurations
from dags.repositories.postgres.model_deployment_workflows import training_approved, training_rejected
from dags.services.airflow_operators import no_action

@task.branch(task_id="train_callback")
def train_callback(**context) -> str:
    configurations = TrainCallbackConfigurations.from_context(context)
    if configurations.approved:
        training_approved(configurations.workflow_id)
        return start_training_pipeline.__name__
    else:
        training_rejected(configurations.workflow_id)
        return no_action.__name__

def start_training_pipeline() -> TriggerDagRunOperator:
    return TriggerDagRunOperator(
        task_id=start_training_pipeline.__name__,
        trigger_dag_id="training_pipeline",
        wait_for_completion=False
    )