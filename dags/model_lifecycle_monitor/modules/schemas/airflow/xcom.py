from airflow.sdk.types import TaskInstance
from pydantic import BaseModel, ConfigDict

from dags.model_lifecycle_monitor.repositories.postgres.model_deployment_workflows import has_expired_promote_pending_workflow_with_replacement
from dags.model_lifecycle_monitor.services.tasks import drift_check_task_id

from dags.shared.modules.configs.airflow import DriftMonitorKeys
from dags.shared.modules.schemas.airflow import AirflowTaskContext

class HasDriftXCom(BaseModel):
    model_config = ConfigDict(strict=True)

    drift_detected: bool
    drift_summary: dict

    @classmethod
    def from_context(cls, context: dict) -> "HasDriftXCom":
        ti: TaskInstance = AirflowTaskContext.from_context(context).ti
        return cls(
            drift_detected=ti.xcom_pull(
                task_ids=drift_check_task_id.__name__,
                key=DriftMonitorKeys.DRIFT_DETECTED_KEY,
            ),
            drift_summary=ti.xcom_pull(
                task_ids=drift_check_task_id.__name__,
                key=DriftMonitorKeys.DRIFT_SUMMARY_KEY,
            )
        )
