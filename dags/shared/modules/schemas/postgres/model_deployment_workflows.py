from dataclasses import dataclass

@dataclass(frozen=True)
class ModelDeploymentWorkflowState:
    train_pending = "train_pending"
    promote_pending_replacement = "promote_pending_replacement"
    promote_pending = "promote_pending"