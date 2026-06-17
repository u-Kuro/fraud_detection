from pydantic_settings import BaseSettings, SettingsConfigDict

class Environment(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    # Postgres
    FRAUD_DETECTION_DB_NAME: str

    # S3
    S3_ENDPOINT_URL: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_MLE_BUCKET: str

    ARCHIVE_BATCH_SIZE: int = 50_000

    @property
    def POSTGRES_FRAUD_DB_URL(self) -> str:
        return f"postgresql:///${self.FRAUD_DETECTION_DB_NAME}"

    @property
    def S3_PIPELINE_ARCHIVE_PATH(self) -> str:
        return "pipeline/archive"