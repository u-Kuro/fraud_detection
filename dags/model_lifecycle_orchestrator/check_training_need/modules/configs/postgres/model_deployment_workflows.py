from dataclasses import dataclass

@dataclass(frozen=True)
class ModelDeploymentWorkflowsConfig:
    challenger_model_expiration_days: int = 7