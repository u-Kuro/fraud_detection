from airflow.models import TaskInstance
from pydantic import BaseModel, StrictStr, StrictInt, StrictFloat

from dags.model_lifecycle_orchestrator.on_training_decision.controllers.slack import initialize_promotion_approval
from dags.model_lifecycle_orchestrator.on_training_decision.modules.schemas.airflow.data_keys import TrainModelKeys
from dags.model_lifecycle_orchestrator.on_training_decision.services.tasks import train_model
from dags.shared.modules.configs.airflow.data_keys import ModelDeploymentWorkflowsKeys
from dags.shared.modules.schemas.airflow import TaskContext

class UpdateTrainedModelInfoInWorkflowXCom(BaseModel):
    model_trained_at_iso_datetime: StrictStr
    mlflow_run_id: StrictStr
    model_name: StrictStr
    model_version: StrictInt
    model_dataset_min_iso_datetime: StrictStr
    model_dataset_max_iso_datetime: StrictStr

    @classmethod
    def from_context(cls, context: dict) -> "UpdateTrainedModelInfoInWorkflowXCom":
        ti: TaskInstance = TaskContext.from_context(context).task_instance
        return cls(
            model_trained_at_iso_datetime=ti.xcom_pull(
                task_ids=train_model.__name__,
                key=TrainModelKeys.MODEL_TRAINED_AT_ISO_DATETIME,
            ),
            mlflow_run_id=ti.xcom_pull(
                task_ids=train_model.__name__,
                key=TrainModelKeys.MLFLOW_RUN_ID,
            ),
            model_name=ti.xcom_pull(
                task_ids=train_model.__name__,
                key=TrainModelKeys.MODEL_NAME,
            ),
            model_version=ti.xcom_pull(
                task_ids=train_model.__name__,
                key=TrainModelKeys.MODEL_VERSION,
            ),
            model_dataset_min_iso_datetime=ti.xcom_pull(
                task_ids=train_model.__name__,
                key=TrainModelKeys.MODEL_DATASET_MIN_ISO_DATETIME,
            ),
            model_dataset_max_iso_datetime=ti.xcom_pull(
                task_ids=train_model.__name__,
                key=TrainModelKeys.MODEL_DATASET_MAX_ISO_DATETIME,
            )
        )

class InitializePromotionApprovalXCom(BaseModel):
    model_name: StrictStr
    model_version: StrictInt
    f1_score: StrictFloat
    pr_auc: StrictFloat
    recall: StrictFloat
    precision: StrictFloat

    @classmethod
    def from_context(cls, context: dict) -> "InitializePromotionApprovalXCom":
        ti: TaskInstance = TaskContext.from_context(context).task_instance
        return cls(
            model_name=ti.xcom_pull(
                task_ids=train_model.__name__,
                key=TrainModelKeys.MODEL_NAME,
            ),
            model_version=ti.xcom_pull(
                task_ids=train_model.__name__,
                key=TrainModelKeys.MODEL_VERSION,
            ),
            f1_score=ti.xcom_pull(
                task_ids=train_model.__name__,
                key=TrainModelKeys.MODEL_F1_SCORE,
            ),
            pr_auc=ti.xcom_pull(
                task_ids=train_model.__name__,
                key=TrainModelKeys.MODEL_PR_AUC,
            ),
            recall=ti.xcom_pull(
                task_ids=train_model.__name__,
                key=TrainModelKeys.MODEL_RECALL,
            ),
            precision=ti.xcom_pull(
                task_ids=train_model.__name__,
                key=TrainModelKeys.MODEL_PRECISION,
            ),
        )

class UpdatePromotionPendingWorkflow(BaseModel):
    slack_promotion_approval_message_ts: StrictStr

    @classmethod
    def from_context(cls, context: dict) -> "UpdatePromotionPendingWorkflow":
        ti: TaskInstance = TaskContext.from_context(context).task_instance
        return cls(
            slack_promotion_approval_message_ts=ti.xcom_pull(
                task_ids=initialize_promotion_approval.__name__,
                key=ModelDeploymentWorkflowsKeys.SLACK_PROMOTION_APPROVAL_MESSAGE_TS,
            ),
        )

class UpdatePromotionApproval(BaseModel):
    slack_promotion_approval_message_ts: StrictStr
    model_name: StrictStr
    model_version: StrictInt
    f1_score: StrictFloat
    pr_auc: StrictFloat
    recall: StrictFloat
    precision: StrictFloat

    @classmethod
    def from_context(cls, context: dict) -> "UpdatePromotionApproval":
        ti: TaskInstance = TaskContext.from_context(context).task_instance
        return cls(
            slack_promotion_approval_message_ts=ti.xcom_pull(
                task_ids=initialize_promotion_approval.__name__,
                key=ModelDeploymentWorkflowsKeys.SLACK_PROMOTION_APPROVAL_MESSAGE_TS,
            ),
            model_name=ti.xcom_pull(
                task_ids=train_model.__name__,
                key=TrainModelKeys.MODEL_NAME,
            ),
            model_version=ti.xcom_pull(
                task_ids=train_model.__name__,
                key=TrainModelKeys.MODEL_VERSION,
            ),
            f1_score=ti.xcom_pull(
                task_ids=train_model.__name__,
                key=TrainModelKeys.MODEL_F1_SCORE,
            ),
            pr_auc=ti.xcom_pull(
                task_ids=train_model.__name__,
                key=TrainModelKeys.MODEL_PR_AUC,
            ),
            recall=ti.xcom_pull(
                task_ids=train_model.__name__,
                key=TrainModelKeys.MODEL_RECALL,
            ),
            precision=ti.xcom_pull(
                task_ids=train_model.__name__,
                key=TrainModelKeys.MODEL_PRECISION,
            ),
        )