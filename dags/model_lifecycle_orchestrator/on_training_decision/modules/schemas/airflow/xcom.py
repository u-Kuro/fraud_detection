from airflow.sdk.types import TaskInstance
from pydantic import BaseModel, ConfigDict

from dags.model_lifecycle_orchestrator.on_training_decision.controllers.slack import initialize_promotion_approval
from dags.model_lifecycle_orchestrator.on_training_decision.modules.schemas.airflow.data_keys import TrainModelKeys
from dags.model_lifecycle_orchestrator.on_training_decision.services.tasks import train_model
from dags.shared.modules.configs.airflow.data_keys import ModelDeploymentWorkflowsKeys
from dags.shared.modules.schemas.airflow import AirflowTaskContext

class UpdateTrainedModelInfoInWorkflowXCom(BaseModel):
    model_config = ConfigDict(strict=True)

    model_trained_at_iso_datetime: str
    mlflow_run_id: str
    model_name: str
    model_version: int
    model_dataset_min_iso_datetime: str
    model_dataset_max_iso_datetime: str

    @classmethod
    def from_context(cls, context: dict) -> "UpdateTrainedModelInfoInWorkflowXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
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
    model_config = ConfigDict(strict=True)

    model_name: str
    model_version: int
    f1_score: float
    pr_auc: float
    recall: float
    precision: float

    @classmethod
    def from_context(cls, context: dict) -> "InitializePromotionApprovalXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
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
    model_config = ConfigDict(strict=True)

    promotion_approval_slack_ts: str

    @classmethod
    def from_context(cls, context: dict) -> "UpdatePromotionPendingWorkflow":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            promotion_approval_slack_ts=ti.xcom_pull(
                task_ids=initialize_promotion_approval.__name__,
                key=ModelDeploymentWorkflowsKeys.PROMOTION_APPROVAL_SLACK_TS,
            ),
        )

class UpdatePromotionApproval(BaseModel):
    model_config = ConfigDict(strict=True)

    promotion_approval_slack_ts: str
    model_name: str
    model_version: int
    f1_score: float
    pr_auc: float
    recall: float
    precision: float

    @classmethod
    def from_context(cls, context: dict) -> "UpdatePromotionApproval":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            promotion_approval_slack_ts=ti.xcom_pull(
                task_ids=initialize_promotion_approval.__name__,
                key=ModelDeploymentWorkflowsKeys.PROMOTION_APPROVAL_SLACK_TS,
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