from enum import StrEnum

class NoActionBranches(StrEnum):
    no_drift = "no_drift"
    no_expired_promote_pending_workflow_with_replacement = "no_expired_promote_pending_workflow_with_replacement"

class DispatchTrainingApprovalBranches(StrEnum):
    cold_start = "cold_start"
    drifted = "drifted"

class SetupTrainingApprovalBranches(StrEnum):
    post = "post"
    replace = "replace"