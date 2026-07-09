from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sdk import task

from dags.modules.configs import dags_config
from dags.modules.schemas.airflow import AirflowTaskContext
from dags.modules.schemas.airflow.promotion_callback import PromotionCallbackConfigurations
from dags.repositories.postgres.model_deployment_workflows import promotion_approved, workflow_rejected
from dags.services.airflow_operators import no_action

promotion_callback_task_id = "promotion_callback"
@task.branch(task_id=promotion_callback_task_id)
def promotion_callback(**context) -> str:
    configurations = PromotionCallbackConfigurations.from_context(context)
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
        promotion_approved(configurations.workflow_id)
        task_context.ti.xcom_push(
            key=dags_config.MODEL_DEPLOYMENT_WORKFLOW_ID,
            value=str(configurations.workflow_id)
        )
        return start_promotion_pipeline.__name__
    else:
        workflow_rejected(configurations.workflow_id)
        return no_action.__name__

def start_promotion_pipeline(**context) -> TriggerDagRunOperator:
    task_context = AirflowTaskContext.from_context(context)
    model_deployment_workflow_id = task_context.ti.xcom_pull(
        task_ids=promotion_callback_task_id,
        key=dags_config.MODEL_DEPLOYMENT_WORKFLOW_ID
    )
    return TriggerDagRunOperator(
        task_id=start_promotion_pipeline.__name__,
        trigger_dag_id="promotion_pipeline",
        wait_for_completion=False,
        conf={
            dags_config.MODEL_DEPLOYMENT_WORKFLOW_ID: model_deployment_workflow_id
        }
    )