from enum import Enum

class DriftMonitorKeys(str, Enum):
    DRIFT_DETECTED_KEY = "DRIFT_DETECTED"
    DRIFT_SUMMARY_KEY = "DRIFT_SUMMARY"