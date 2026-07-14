from datetime import datetime

from airflow.sdk import task

from dags.shared.repositories.postgres import postgres_hook
from dags.training_pipeline.modules.schemas.airflow.xcom import UpdateDeploymentWorkflowXCom

@task(task_id="update_deployment_workflow")
def update_deployment_workflow(**context) -> None:
    update_deployment_workflow_xcom = UpdateDeploymentWorkflowXCom.from_context(context)

    postgres_hook.run("""
        UPDATE model_deployment_workflows
        SET trained_at = %(trained_at)s,
            mlflow_run_id = %(mlflow_run_id)s,
            registered_model_name = %(registered_model_name)s,
            registered_model_version = %(registered_model_version)s,
            model_dataset_min_timestamp = %(model_dataset_min_timestamp)s,
            model_dataset_max_timestamp = %(model_dataset_max_timestamp)s
        WHERE id = %(id)s
        """, parameters={
            "id": update_deployment_workflow_xcom.workflow_id,
            "trained_at": datetime.fromisoformat(update_deployment_workflow_xcom.model_trained_at_iso_datetime),
            "mlflow_run_id": update_deployment_workflow_xcom.mlflow_run_id,
            "registered_model_name": update_deployment_workflow_xcom.model_name,
            "registered_model_version": update_deployment_workflow_xcom.model_version,
            "model_dataset_min_timestamp": datetime.fromisoformat(update_deployment_workflow_xcom.model_dataset_min_iso_datetime),
            "model_dataset_max_timestamp": datetime.fromisoformat(update_deployment_workflow_xcom.model_dataset_max_iso_datetime),
        }
    )