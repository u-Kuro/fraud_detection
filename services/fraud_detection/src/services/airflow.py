import httpx

from services.shared.modules.configs import AirflowConfig
from services.shared.modules.environment import airflow_environment

def trigger_airflow_dag(dag_id: str, configurations: dict) -> None:
    httpx.post(
        f"{AirflowConfig.MWAA_WEBSERVER_URL}/api/v1/dags/{dag_id}/dagRuns",
        json={"conf": configurations},
        auth=(airflow_environment.AIRFLOW_USERNAME, airflow_environment.AIRFLOW_PASSWORD),
        verify=False,
        timeout=5.0,
    ).raise_for_status()
