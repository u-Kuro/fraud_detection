from pydantic_settings import BaseSettings, SettingsConfigDict

class S3Environment(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    # AWS_DEFAULT_REGION: str
    # AWS_ENDPOINT_URL_S3: str
    # AWS_ACCESS_KEY_ID: str
    # AWS_SECRET_ACCESS_KEY: str
    S3_BUCKET_NAME: str

s3_environment = S3Environment()