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

    # MLflow
    MLFLOW_TRACKING_URI: str
    MLFLOW_EXPERIMENT_NAME: str = "fraud-detection"

    # Slack
    SLACK_BOT_USER_AUTH_TOKEN: str
    SLACK_CHANNEL_ID: str

    # Internal fraud_api URL for post-promotion hot-reload
    FRAUD_API_URL: str = "http://fraud-detection:30000"

    # Training hyperparams
    MAX_SELECTED_ROWS: int = 100_000
    TRAINING_MINIMUM_ROWS: int = 1_000
    RANDOM_STATE: int = 42
    TEST_SIZE: float = 0.2
    VAL_SIZE: float = 0.2
    BAYES_STEPS: int = 30
    TRAINING_TIMEOUT_SECONDS: int = 3600

    @property
    def POSTGRES_FRAUD_DB_URL(self) -> str:
        return f"postgresql:///${self.FRAUD_DETECTION_DB_NAME}"

    @property
    def S3_PIPELINE_REFERENCE_PATH(self) -> str:
        return "pipeline/reference"

    @property
    def S3_PIPELINE_DATASETS_PATH(self) -> str:
        return "pipeline/datasets"

environment = Environment()
