from pydantic import StrictStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class MWAAEnvironment(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    # AWS_DEFAULT_REGION: StrictStr
    # AWS_ENDPOINT_URL_MWAA: StrictStr
    # AWS_ACCESS_KEY_ID: StrictStr
    # AWS_SECRET_ACCESS_KEY: StrictStr
    MWAA_ENVIRONMENT_NAME: StrictStr

mwaa_environment = MWAAEnvironment()