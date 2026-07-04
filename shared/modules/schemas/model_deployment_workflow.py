from enum import Enum

class ModelDeploymentWorkflowState(str, Enum):
    train_pending = "train_pending"
    promote_pending = "promote_pending"