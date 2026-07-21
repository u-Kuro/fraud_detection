from dataclasses import dataclass

@dataclass(frozen=True)
class DriftMonitorKeys:
    DRIFT_DETECTED: str = "DRIFT_DETECTED"
    DRIFT_SUMMARY: str = "DRIFT_SUMMARY"