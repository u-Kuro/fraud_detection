from services.fraud_detection.src.repositories.mwaa.mwaa import mwaa_client
from services.shared.modules.environment.airflow import airflow_environment

def trigger_airflow_dag(dag_id: str, configurations: dict) -> None:
    response = mwaa_client.invoke_rest_api(
        Name=airflow_environment.MWAA_ENVIRONMENT_NAME,
        Path=f"/dags/{dag_id}/dagRuns",
        Method="POST",
        Body={"conf": configurations},
    )

    status_code = response.get("RestApiStatusCode")
    if not (200 <= status_code < 300):
        raise RuntimeError(
            f"Unexpected status code {status_code} triggering DAG '{dag_id}'. "
            f"Response: {response.get('RestApiResponse')}"
        )
