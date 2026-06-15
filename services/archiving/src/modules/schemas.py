from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    FRAUD_DETECTION_DB_NAME: str

    S3_ENDPOINT_URL: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_MODEL_DATASETS_BUCKET: str = "model-datasets"

    ARCHIVE_BATCH_SIZE: int = 50_000

    @property
    def postgres_fraud_database_url(self) -> str:
        return f"postgresql:///${self.FRAUD_DETECTION_DB_NAME}"