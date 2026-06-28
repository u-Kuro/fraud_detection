import httpx

from shared.modules.configs import airflow_config
from shared.modules.environment import airflow_environment
from shared.modules.logging import logger

def trigger_airflow_dag(dag_id: str, configurations: dict) -> None:
    try:
        httpx.post(
            f"{airflow_config.MWAA_WEBSERVER_URL}/api/v1/dags/{dag_id}/dagRuns",
            json={"conf": configurations},
            auth=(airflow_environment.AIRFLOW_USERNAME, airflow_environment.AIRFLOW_PASSWORD),
            verify=False,
            timeout=5.0,
        ).raise_for_status()
    except Exception as exc:
        logger.warning(f"Airflow trigger for {dag_id} failed (non-fatal): {exc}")
