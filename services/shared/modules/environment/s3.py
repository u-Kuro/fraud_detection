from pydantic_settings import BaseSettings, SettingsConfigDict

class S3Environment(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    S3_BUCKET_NAME: str

s3_environment = S3Environment()