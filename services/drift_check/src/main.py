from services.drift_check.src.modules.configs.airflow.xcom import DriftCheckXComKeys
from services.drift_check.src.services.evidently import drift_check
from services.shared.controllers.airflow.xcom import xcom_push

def main() -> None:
    drift_detected, drift_summary = drift_check()
    xcom_push({
        DriftCheckXComKeys.drift_detected: drift_detected,
        DriftCheckXComKeys.drift_summary: drift_summary
    })

if __name__ == "__main__":
    main()