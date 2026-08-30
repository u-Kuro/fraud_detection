from datetime import datetime

from airflow.models import TaskInstance
from pydantic import BaseModel, ConfigDict

from dags.model_lifecycle_orchestrator.on_promotion_decision.modules.configs.airflow.data_keys import ArchiveKeys
from dags.model_lifecycle_orchestrator.on_promotion_decision.repositories.postgres.model_deployments import promote_model_deployment
from dags.shared.modules.schemas.airflow import TaskContext

class ArchiveUsedTransactionInferencesXCom(BaseModel):
    model_config = ConfigDict(strict=False)

    transaction_inferences_archive_cutoff_iso_datetime: datetime

    @classmethod
    def from_context(cls, context: dict) -> "ArchiveUsedTransactionInferencesXCom":
        ti: TaskInstance = TaskContext.from_context(context).task_instance
        return cls(
            transaction_inferences_archive_cutoff_iso_datetime=ti.xcom_pull(
                task_ids=promote_model_deployment.__name__,
                key=ArchiveKeys.TRANSACTION_INFERENCES_ARCHIVE_CUTOFF_ISO_DATETIME,
            )
        )