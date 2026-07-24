from uuid import UUID

from pydantic import BaseModel, ConfigDict

from dags.shared.modules.schemas.airflow import AirflowDAGRunConfigurationsContext

class TrainingCallbackConfigurations(BaseModel):
    model_config = ConfigDict(strict=False)

    approved: bool
    workflow_id: UUID
    for_promotion: bool

    @classmethod
    def from_context(cls, context: dict) -> "TrainingCallbackConfigurations":
        return cls.model_validate(AirflowDAGRunConfigurationsContext.from_context(context).conf)