from services.drift_check.src.modules.configs.airflow.data_keys import DriftMonitorKeys
from services.drift_check.src.services.evidently import drift_check
from services.shared.controllers.airflow.xcom import xcom_push

def main() -> None:
    drift_detected, drift_summary = drift_check()
    xcom_push({
        DriftMonitorKeys.DRIFT_DETECTED_KEY: drift_detected,
        DriftMonitorKeys.DRIFT_SUMMARY_KEY: drift_summary
    })

if __name__ == "__main__":
    main()