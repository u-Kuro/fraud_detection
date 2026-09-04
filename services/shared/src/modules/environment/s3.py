from pydantic import StrictStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class S3Environment(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    # AWS_DEFAULT_REGION: StrictStr
    # AWS_ENDPOINT_URL_S3: StrictStr
    # AWS_ACCESS_KEY_ID: StrictStr
    # AWS_SECRET_ACCESS_KEY: StrictStr
    S3_BUCKET_NAME: StrictStr

s3_environment = S3Environment()