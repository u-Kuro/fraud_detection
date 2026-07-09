from services.drift_monitor.src.services.evidently import check_for_drift
from shared.controllers.airflow.xcom import xcom_push

def main() -> None:
    drift_detected, drift_summary = check_for_drift()
    xcom_push({
        "drift_detected": drift_detected,
        "drift_summary": drift_summary
    })

if __name__ == "__main__":
    main()