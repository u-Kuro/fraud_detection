from pydantic_settings import BaseSettings, SettingsConfigDict

class AirflowEnvironment(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_ENDPOINT_URL_MWAA: str
    MWAA_ENVIRONMENT_NAME: str

airflow_environment = AirflowEnvironment()