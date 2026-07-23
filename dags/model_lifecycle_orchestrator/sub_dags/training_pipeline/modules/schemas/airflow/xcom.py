from typing import Any

from airflow.sdk.types import TaskInstance
from pydantic import BaseModel, ConfigDict

from dags.shared.modules.configs.airflow import ModelDeploymentWorkflowsKeys
from dags.shared.modules.schemas.airflow import AirflowTaskContext
from dags.model_lifecycle_orchestrator.sub_dags.training_pipeline.modules.configs.airflow.data_keys import TrainingPipelineKeys
from dags.model_lifecycle_orchestrator.sub_dags.training_pipeline.services.training_pipeline import train_model_task_id

class UpdateDeploymentWorkflowXCom(BaseModel):
    model_config = ConfigDict(strict=False)

    workflow_id: str
    model_trained_at_iso_datetime: str
    mlflow_run_id: str
    model_name: str
    model_version: int
    model_dataset_min_iso_datetime: str
    model_dataset_max_iso_datetime: str
    model_metrics: dict[str, Any]

    @classmethod
    def from_context(cls, context: dict) -> "UpdateDeploymentWorkflowXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            workflow_id=ti.xcom_pull(
                # TODO - Need to be in callback (removed in services)
                task_ids=train_model_task_id,
                key=ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID,
            ),
            model_trained_at_iso_datetime=ti.xcom_pull(
                task_ids=train_model_task_id,
                key=TrainingPipelineKeys.MODEL_TRAINED_AT_ISO_DATETIME,
            ),
            mlflow_run_id=ti.xcom_pull(
                task_ids=train_model_task_id,
                key=TrainingPipelineKeys.MLFLOW_RUN_ID,
            ),
            model_name=ti.xcom_pull(
                task_ids=train_model_task_id,
                key=TrainingPipelineKeys.MODEL_NAME,
            ),
            model_version=ti.xcom_pull(
                task_ids=train_model_task_id,
                key=TrainingPipelineKeys.MODEL_VERSION,
            ),
            model_dataset_min_iso_datetime=ti.xcom_pull(
                task_ids=train_model_task_id,
                key=TrainingPipelineKeys.MODEL_DATASET_MIN_ISO_DATETIME,
            ),
            model_dataset_max_iso_datetime=ti.xcom_pull(
                task_ids=train_model_task_id,
                key=TrainingPipelineKeys.MODEL_DATASET_MAX_ISO_DATETIME,
            ),
            model_metrics=ti.xcom_pull(
                task_ids=train_model_task_id,
                key=TrainingPipelineKeys.MODEL_METRICS,
            ),
        )