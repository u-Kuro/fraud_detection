from enum import StrEnum

class DispatchTrainingApprovalBranches(StrEnum):
    cold_start = "cold_start"
    drifted = "drifted"

class SetupTrainingApprovalBranches(StrEnum):
    post = "post"
    replace = "replace"