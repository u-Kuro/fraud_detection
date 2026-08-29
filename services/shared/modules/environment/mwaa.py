from pydantic_settings import BaseSettings, SettingsConfigDict

class MWAAEnvironment(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    # AWS_DEFAULT_REGION: str
    # AWS_ENDPOINT_URL_MWAA: str
    # AWS_ACCESS_KEY_ID: str
    # AWS_SECRET_ACCESS_KEY: str
    MWAA_ENVIRONMENT_NAME: str

mwaa_environment = MWAAEnvironment()