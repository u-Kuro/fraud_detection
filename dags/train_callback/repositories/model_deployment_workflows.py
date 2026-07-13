from airflow.sdk import task

from dags.shared.repositories.postgres import postgres_hook
from dags.train_callback.modules.schemas.airflow.xcom import UpdateTrainingWorkflowXCom
from dags.train_callback.services.training_callback import start_training_pipeline

@task.branch(task_id="update_approved_training_workflow")
def update_approved_training_workflow(**context) -> str:
    update_training_workflow_xcom = UpdateTrainingWorkflowXCom.from_context(context)

    postgres_hook.run("""
        UPDATE model_deployment_workflows
        SET training_approved = %(training_approved)s
        WHERE id = %(id)s
        """, parameters={
            "id": update_training_workflow_xcom.workflow_id,
            "training_approved": True
        }
    )

    return start_training_pipeline.__name__

@task.branch(task_id="delete_rejected_training_workflow")
def delete_rejected_training_workflow(**context):
    update_training_workflow_xcom = UpdateTrainingWorkflowXCom.from_context(context)

    postgres_hook.run("""
        DELETE FROM model_deployment_workflows 
        WHERE id = %(id)s
        """, parameters={
            "id": update_training_workflow_xcom.workflow_id
        }
    )