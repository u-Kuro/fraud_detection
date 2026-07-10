from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sdk import task

from dags.promotion_callback.repositories.postgres import training_approved, workflow_rejected
from dags.train_callback.modules.schemas.airflow.configurations import TrainingCallbackConfigurations

from dags.shared.modules.configs.airflow import ModelDeploymentWorkflowsKeys
from dags.shared.modules.schemas.airflow import AirflowTaskContext
from dags.shared.services.airflow_operators import no_action

training_callback_task_id = "training_callback"
@task.branch(task_id=training_callback_task_id)
def training_callback(**context) -> str:
    configurations = TrainingCallbackConfigurations.from_context(context)
    if configurations.approved:
        task_context = AirflowTaskContext.from_context(context)
        # TODO - try and check if PostgresHook()
        # hook = PostgresHook(postgres_conn_id="mle_postgres")
        #
        #     # get_records() for simple iteration
        #     rows = hook.get_records("""
        #         SELECT model_version, AVG(score), COUNT(*)
        #         FROM   predictions
        #         WHERE  predicted_at >= NOW() - INTERVAL '1 hour'
        #         GROUP  BY model_version
        #     """)
        #
        #     return {"versions": [dict(zip(["version","avg_score","count"], r)) for r in rows]}
        # created aws_secretsmanager_secret name is "airflow/connections/mle_postgres"
        training_approved(configurations.workflow_id)
        task_context.ti.xcom_push(
            key=ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID_KEY,
            value=str(configurations.workflow_id)
        )
        return start_training_pipeline.__name__
    else:
        workflow_rejected(configurations.workflow_id)
        return no_action.__name__

def start_training_pipeline(**context) -> TriggerDagRunOperator:
    task_context = AirflowTaskContext.from_context(context)
    model_deployment_workflow_id = task_context.ti.xcom_pull(
        task_ids=training_callback_task_id,
        key=ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID_KEY
    )
    return TriggerDagRunOperator(
        task_id=start_training_pipeline.__name__,
        trigger_dag_id="training_pipeline",
        wait_for_completion=False,
        conf={
            ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID_KEY: model_deployment_workflow_id
        }
    )