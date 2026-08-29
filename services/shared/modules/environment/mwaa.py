from pydantic_settings import BaseSettings, SettingsConfigDict

class MWAAEnvironment(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    MWAA_ENVIRONMENT_NAME: str

mwaa_environment = MWAAEnvironment()