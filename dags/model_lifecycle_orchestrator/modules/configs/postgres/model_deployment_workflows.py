from dataclasses import dataclass

@dataclass(frozen=True)
class ModelDeploymentWorkflowsConfig:

    trained_model_expiration_days: int = 7