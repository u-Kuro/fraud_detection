from services.drift_check.src.modules.configs.airflow.data_keys import DriftCheckKeys
from services.drift_check.src.services.evidently import drift_check
from services.shared.controllers.airflow.xcom import xcom_push

def main() -> None:
    drift_detected, drift_summary = drift_check()
    xcom_push({
        DriftCheckKeys.DRIFT_DETECTED: drift_detected,
        DriftCheckKeys.DRIFT_SUMMARY: drift_summary
    })

if __name__ == "__main__":
    main()