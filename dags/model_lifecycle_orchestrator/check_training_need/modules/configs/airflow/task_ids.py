from enum import StrEnum

from dags.model_lifecycle_orchestrator.check_training_need.services.tasks import no_action, dispatch_training_approval, setup_training_approval

class NoActionTaskIDs(StrEnum):
    no_drift = f"{no_action.__name__}.no_drift"
    no_expired_promote_pending_workflow_with_replacement = f"{no_action.__name__}.no_expired_promote_pending_workflow_with_replacement"
    no_expired_workflows = f"{no_action.__name__}.no_expired_workflows"

class DispatchTrainingApprovalTaskIDs(StrEnum):
    cold_start = f"{dispatch_training_approval.__name__}.cold_start"
    drifted = f"{dispatch_training_approval.__name__}.drifted"

class SetupTrainingApprovalTaskIDs(StrEnum):
    post = f"{setup_training_approval.__name__}.post"
    replace = f"{dispatch_training_approval.__name__}.replace"