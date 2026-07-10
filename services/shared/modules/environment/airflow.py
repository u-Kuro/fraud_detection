from pydantic_settings import BaseSettings, SettingsConfigDict

class AirflowEnvironment(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    AIRFLOW_USERNAME: str
    AIRFLOW_PASSWORD: str

airflow_environment = AirflowEnvironment()