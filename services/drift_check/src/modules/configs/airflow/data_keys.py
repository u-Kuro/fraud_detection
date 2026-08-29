from dataclasses import dataclass

@dataclass(frozen=True)
class DriftCheckKeys:
    DRIFT_DETECTED: str = "DRIFT_DETECTED"
    DRIFT_SUMMARY: str = "DRIFT_SUMMARY"
    # ACTIVE_MODEL_DEPLOYMENT_MLFLOW_RUN_ID: str = "ACTIVE_MODEL_DEPLOYMENT_MLFLOW_RUN_ID"