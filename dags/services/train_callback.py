from airflow.sdk import task

from dags.modules.schemas.configurations import TrainCallbackConfigurations
from dags.repositories.postgres.model_deployment_workflows import training_approved, training_rejected

@task
def train_callback(**context):
    configurations = TrainCallbackConfigurations.from_context(context)
    if configurations.approved:
        training_approved(configurations.workflow_id)
    else:
        training_rejected(configurations.workflow_id)