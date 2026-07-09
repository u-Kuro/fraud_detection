from pydantic import BaseModel, ConfigDict

class DriftMonitorKeysConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    DRIFT_DETECTED_KEY: str = "DRIFT_DETECTED"
    DRIFT_SUMMARY_KEY: str = "DRIFT_SUMMARY"

drift_monitor_keys_config = DriftMonitorKeysConfig()