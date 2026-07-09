from pydantic import BaseModel, ConfigDict

class PromotionPipelineConfigurations(BaseModel):
    model_config = ConfigDict(strict=True)

    model_deployment_workflow_id: str

    @classmethod
    def from_context(cls, context: dict) -> "PromotionPipelineConfigurations":
        return cls(**(context["dag_run"].conf or {}))