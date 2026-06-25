from pydantic import BaseModel, ConfigDict

class AirflowConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    MWAA_WEBSERVER_URL: str = "http://airflow-webserver:8080"

airflow_config = AirflowConfig()