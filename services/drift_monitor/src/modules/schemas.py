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

    # Slack
    SLACK_BOT_USER_AUTH_TOKEN: str
    SLACK_CHANNEL_ID: str

    # Drift thresholds
    MAX_SELECTED_ROWS: int = 50_000
    DRIFT_THRESHOLD: float = 0.5
    MINIMUM_ROWS: int = 500
    LOOKBACK_DAYS: int = 7

    @property
    def POSTGRES_FRAUD_DB_URL(self) -> str:
        return f"postgresql:///${self.FRAUD_DETECTION_DB_NAME}"

    @property
    def S3_PIPELINE_REFERENCE_PATH(self) -> str:
        return "pipeline/reference"

    @property
    def S3_PIPELINE_DRIFT_REPORTS_PATH(self) -> str:
        return "pipeline/drift-reports"