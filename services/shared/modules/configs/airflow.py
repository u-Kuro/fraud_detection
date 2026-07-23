from dataclasses import dataclass

@dataclass(frozen=True)
class AirflowConfig:
    MWAA_WEBSERVER_URL: str = "http://airflow-webserver:8080"