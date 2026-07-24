# from pydantic import BaseModel, ConfigDict
#
# class TrainingPipelineConfigurations(BaseModel):
#     model_config = ConfigDict(strict=True)
#
#     model_deployment_workflow_id: str
#
#     @classmethod
#     def from_context(cls, context: dict) -> "TrainingPipelineConfigurations":
#         return cls(**(context["dag_run"].conf or {}))