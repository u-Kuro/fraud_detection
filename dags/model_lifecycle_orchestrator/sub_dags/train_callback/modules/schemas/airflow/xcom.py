from airflow.sdk.types import TaskInstance
from pydantic import BaseModel, ConfigDict

from dags.shared.modules.configs.airflow import ModelDeploymentWorkflowsKeys
from dags.shared.modules.schemas.airflow import AirflowTaskContext
from dags.model_lifecycle_orchestrator.sub_dags.train_callback.repositories.model_deployment_workflows import update_approved_training_workflow
from dags.model_lifecycle_orchestrator.sub_dags.train_callback.services.training_callback import training_callback_task_id

class UpdateTrainingWorkflowXCom(BaseModel):
    model_config = ConfigDict(strict=True)

    workflow_id: str

    @classmethod
    def from_context(cls, context: dict) -> "UpdateTrainingWorkflowXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            workflow_id=ti.xcom_pull(
                task_ids=training_callback_task_id,
                key=ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID_KEY,
            )
        )

class StartTrainingPipelineXCom(BaseModel):
    model_config = ConfigDict(strict=True)

    workflow_id: str

    @classmethod
    def from_context(cls, context: dict) -> "StartTrainingPipelineXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            workflow_id=ti.xcom_pull(
                task_ids=update_approved_training_workflow.__name__,
                key=ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID_KEY,
            )
        )