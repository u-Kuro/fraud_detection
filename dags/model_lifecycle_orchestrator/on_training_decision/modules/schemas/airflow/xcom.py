from datetime import datetime

from pydantic import BaseModel, StrictStr, StrictInt, StrictFloat, model_validator

from dags.model_lifecycle_orchestrator.on_training_decision.modules.configs.airflow.xcom import TrainModelXComKeys
from dags.model_lifecycle_orchestrator.on_training_decision.services.tasks import train_model_operator
from dags.shared.modules.schemas.airflow import TaskContext

class TrainModelResult(BaseModel):
    model_trained_at_datetime: StrictStr
    model_mlflow_run_id: StrictStr
    model_name: StrictStr
    model_version: StrictInt
    model_dataset_min_datetime: datetime
    model_dataset_max_datetime: datetime
    model_f1_score: StrictFloat
    model_pr_auc: StrictFloat
    model_recall: StrictFloat
    model_precision: StrictFloat

    @model_validator(mode="wrap")
    @classmethod
    def parse_xcom(cls, context: TaskContext) -> "TrainModelResult":
        task_instance = context.task_instance
        task_id = context.resolve_task_id(train_model_operator.__name__)
        return cls(
            model_trained_at_datetime=task_instance.xcom_pull(
                task_ids=task_id,
                key=TrainModelXComKeys.model_trained_at_datetime,
            ),
            model_mlflow_run_id=task_instance.xcom_pull(
                task_ids=task_id,
                key=TrainModelXComKeys.model_mlflow_run_id,
            ),
            model_name=task_instance.xcom_pull(
                task_ids=task_id,
                key=TrainModelXComKeys.model_name,
            ),
            model_version=task_instance.xcom_pull(
                task_ids=task_id,
                key=TrainModelXComKeys.model_version,
            ),
            model_dataset_min_datetime=task_instance.xcom_pull(
                task_ids=task_id,
                key=TrainModelXComKeys.model_dataset_min_datetime,
            ),
            model_dataset_max_datetime=task_instance.xcom_pull(
                task_ids=task_id,
                key=TrainModelXComKeys.model_dataset_max_datetime,
            ),
            model_f1_score=task_instance.xcom_pull(
                task_ids=task_id,
                key=TrainModelXComKeys.model_f1_score,
            ),
            model_pr_auc=task_instance.xcom_pull(
                task_ids=task_id,
                key=TrainModelXComKeys.model_pr_auc,
            ),
            model_recall=task_instance.xcom_pull(
                task_ids=task_id,
                key=TrainModelXComKeys.model_recall,
            ),
            model_precision=task_instance.xcom_pull(
                task_ids=task_id,
                key=TrainModelXComKeys.model_precision,
            ),
        )